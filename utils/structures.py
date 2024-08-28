import os
import pathlib
from pwd import getpwuid
from grp import getgrgid


from utils.icons import identify_icon, Icons
from utils.colours import row_highlight_colour
from utils.enums import Modes


class Popup:
    def __init__(self,
        options: list,  # {text: str, callback: Callable},
        title: str = None,
        description: str = None,
        mode_on_close: Modes = Modes.default,
        selection: int = 0
    ) -> None:
        self.options = options
        self.title = title
        self.description = description
        self.mode_on_close = mode_on_close
        self.retain_selection = selection
        self.height, self.width, self.top, self.left = 0, 0, 0, 0

    def set_dimensions(self, available_height, available_width):
        # Width should be 1/2 of the screen, at least 10 and at most 80
        self.width = min(max(available_width // 2, 10), 80)
        # Height should be 1/2 of the screen, at least 5 and at most 7
        self.height = min(max(available_height // 2, 5), 7)
        # Top should be 1/4 of the screen
        self.top = (available_height - self.height) // 2
        # Left should be 1/4 of the screen
        self.left = (available_width - self.width) // 2

    @property
    def json(self):
        return [self.height, self.width, self.top, self.left]

    def __getattribute__(self, name: str):
        return super().__getattribute__(name)


class Item:
    def __init__(self, path: pathlib.Path | str, name: str):
        self.path = pathlib.Path(path)
        self.name = name
        self.location = self.path / name
        self.is_parent = False
        if name == "..":
            self.name = "Parent Directory"
            self.location = self.path.parent
            self.is_parent = True
        self.is_dir = os.path.isdir(self.location)
        self.is_link = os.path.islink(self.location)
        self.link_from = None
        if self.is_link:
            try:
                self.link_from = os.path.realpath(self.location)
                os.stat(self.link_from)  # Test if the link is broken
            except FileNotFoundError:
                self._icon = Icons.file.broken_link
                self.is_dir = False
                self._size = 0
                self._permissions = [0, 0, 0]
                self._modified = 0
                self._owner = "Unknown"
                self._group = "Unknown"
                return
            except PermissionError:
                self.link_from = None
            self.is_dir = os.path.isdir(self.link_from or self.location)

        self._size = None
        self._permissions = None
        self._modified = None
        self._owner = None
        self._group = None
        self._icon = None
        self._stat = None

    @property
    def size(self):
        if self._size is None:
            self._size = 0
            if not self.is_dir:
                try:
                    self._size = os.path.getsize(self.link_from or self.location)
                except (FileNotFoundError, PermissionError):
                    self._size = 0
        return self._size

    @property
    def permissions(self):
        if self._permissions is None:
            raw_permissions = self.stat.st_mode
            octal_permissions = oct(raw_permissions)[-3:]
            self._permissions = [int(octal_permissions[0]), int(octal_permissions[1]), int(octal_permissions[2])]
        return self._permissions

    @property
    def modified(self):
        if self._modified is None:
            try:
                self._modified = os.path.getmtime(self.link_from or self.location)
            except (FileNotFoundError, PermissionError):
                self._modified = 0
        return self._modified

    @property
    def owner(self):
        if self._owner is None:
            owner_id = self.stat.st_uid
            self._owner = getpwuid(owner_id).pw_name
        return self._owner

    @property
    def stat(self):
        if self._stat is None:
            try:
                self._stat = os.stat(self.link_from or self.location)
            except (FileNotFoundError, PermissionError):
                self._stat = os.stat("/")
                self._icon = Icons.generic.cross
        return self._stat

    @property
    def icon(self):
        if self._icon is None:
            self._icon = identify_icon(self)
        return self._icon

    @property
    def group(self):
        if self._group is None:
            group_id = self.stat.st_gid
            self._group = getgrgid(group_id).gr_name
        return self._group

    @property
    def can_read(self):
        # If the current user is the owner of the file
        if self.owner == os.getlogin():
            return self.permissions[0] >= 4
        # If the current user is in the same group as the file
        if self.group == os.getlogin():
            return self.permissions[1] >= 4
        # If the current user is not the owner or in the same group as the file
        return self.permissions[2] >= 4

    @property
    def display(self):
        return f"  {self.icon} {self.name}"

    def row_colour(self, selected_name: str):
        return row_highlight_colour(self, self.location == selected_name)

    def __str__(self) -> str:
        return self.name

    # Allow for doing Item[:8] to get the first 8 characters of the name
    def __getitem__(self, item: int) -> str:
        return self.name[item]

    def __len__(self) -> int:
        return len(self.name)

    def __divmod__(self, other: str):
        # Runs when the object is divided by a string
        return Item(self.location / other)
