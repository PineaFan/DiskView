import os
import pathlib
from pwd import getpwuid
from grp import getgrgid


from utils.icons import identify_icon, Icons
from utils.colours import row_highlight_colour


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
                self.icon = Icons.file.broken_link
                self.is_dir = False
                self.size = 0
                self.permissions = [0, 0, 0]
                self.modified = 0
                self.created = 0
                self.owner = "Unknown"
                self.group = "Unknown"
                return
            self.is_dir = os.path.isdir(self.link_from or self.location)
        self.size = 0
        stat = os.stat(self.link_from or self.location)
        raw_permissions = stat.st_mode
        octal_permissions = oct(raw_permissions)[-3:]
        self.permissions = [int(octal_permissions[0]), int(octal_permissions[1]), int(octal_permissions[2])]
        self.modified = os.path.getmtime(self.link_from or self.location)

        owner_id = stat.st_uid
        self.owner = getpwuid(owner_id).pw_name
        group_id = stat.st_gid
        self.group = getgrgid(group_id).gr_name

        self.icon = identify_icon(self)


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
