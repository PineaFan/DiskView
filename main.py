import platform
if platform.system().lower() == "windows":
    print("Windows is not supported (Due to differing file permissions and Curses breaking entirely)")
    exit(1)

import pathlib
import os
import sys
import curses
import time

from pages import sidebar
from pages import files
from pages import header
from pages import preview
from pages import footer

from utils.enums import Modes
from utils.colours import Colours
from utils.structures import Item
from utils.keymap import Keys


class GridHelper:
    def __init__(self, height: int, width: int, padding: bool = True):
        self.sections = {}
        self.width = width
        self.height = height
        if padding:
            self.remaining = [height - 2, width - 2, 1, 1]
        else:
            self.remaining = [height, width, 0, 0]
        self.padding = padding

    @property
    def json(self):
        return self.sections

    def add_section(self, name, height=None, width=None, flip_align=False, maximum=None, minimum=None, within=None):
        """
        Either width or height must be provided. If both are provided, width will be used.
        If an integer is provided, it will be used as the width or height.
        If a float is provided, it will be used as a fraction of the total screen, rounded down.
        flip_align will align the section to the bottom or right, rather than the top or left.
        within will align the section within another section, rather than the remaining space.
        """

        # If "within" is provided, remaining space should be based on that section, rather than unused space
        remaining = self.sections[within] if within else self.remaining
        def update(index, amount, negative=True):
            amount += (1 if self.padding else 0)
            amount *= (-1 if negative else 1 )
            if within:
                self.sections[within][index] += amount
            else:
                self.remaining[index]  += amount

        maximum, minimum = maximum or float("inf"), minimum or 0
        if width is None and height is None:
            # Use the remaining space
            width, height = remaining[1], remaining[0]
        if width is not None and height is not None:
            height = None
        if width and width < 0:
            width = remaining[1] + width - (1 if self.padding else 0)
        if height and height < 0:
            height = remaining[0] + height - (1 if self.padding else 0)

        if width:
            if isinstance(width, float):
                width = int(width * remaining[1])
            width = max(minimum, min(width, maximum))
        else:
            if isinstance(height, float):
                height = int(height * remaining[0])
            height = max(minimum, min(height, maximum))
        if width and width > remaining[1]:
            raise ValueError("Section width exceeds remaining space.")
        if height and height > remaining[0]:
            raise ValueError("Section height exceeds remaining space.")

        if height and not flip_align:
            # Align to the top
            self.sections[name] = [height, remaining[1], remaining[2], remaining[3]]
            # Remove the height from the remaining space, and update the top position
            update(0, height)
            update(2, height, negative=False)
        elif height and flip_align:
            # Align to the bottom
            self.sections[name] = [height, remaining[1], remaining[2] + remaining[0] - height, remaining[3]]
            # Remove the height from the remaining space
            update(0, height)
        elif width and not flip_align:
            # Align to the left
            self.sections[name] = [remaining[0], width, remaining[2], remaining[3]]
            # Remove the width from the remaining space, and update the left position
            update(1, width)
            update(3, width, negative=False)
        elif width and flip_align:
            # Align to the right
            self.sections[name] = [remaining[0], width, remaining[2], remaining[3] + remaining[1] - width]
            # Remove the width from the remaining space
            update(1, width)

    def add_remaining(self, name):
        self.sections[name] = self.remaining

    def __getattribute__(self, name: str) -> any:
        if name in ["add_section", "add_remaining", "json", "sections", "width", "height", "padding", "remaining"] or name.startswith("__"):
            return super().__getattribute__(name)
        return self.sections[name]


class Explorer:
    def __init__(self, screen, start_path=None):
        self.current_path = start_path or pathlib.Path.home()
        self.current_item = None
        self.selection = 0
        self.to_highlight = None
        self.folder_details = None
        self.scroll_direction_down = True

        self.username = os.getlogin()
        self.groups = os.getgroups()
        self.memo = {
            "can_read": {}
        }
        self.known_files = {}
        self.mode = Modes.default

        self.settings = {
            "show_hidden_files": False,
            "show_permission_denied": True,
            "show_preview": True,
            "use_numeric_jump": False
        }

        self.screen = screen
        curses.curs_set(0)

        self.size_last_frame = 0
        self.sections = None
        self.resize_hook()

        # Define the colours
        self.colours = Colours()

        self.mode_focus = {
            Modes.default: "main",
            Modes.search: "footer"
        }

        self.search = ""
        self.search_index = 0

    @property
    def modules(self):
        modules = {
            "main": files,
            "header": header,
            "sidebar": sidebar,
            "footer": footer
        }
        if self.settings.get("show_preview", True):
            modules["preview"] = preview
        return modules

    @property
    def items(self):
        # Returns a list of items in the current directory
        if self.current_path in self.known_files:
            path = self.known_files[self.current_path]
            folders, files = path["folders"], path["files"]
            if self.search:
                folders = [x for x in folders if self.search.lower() in x.name.lower()]
                files = [x for x in files if self.search.lower() in x.name.lower()]
            return folders + files
        items = []
        for item in self.current_path.iterdir():
            items.append(Item(self.current_path, item.name))
        folders, files = [x for x in items if x.is_dir], [x for x in items if not x.is_dir]

        # Filter out hidden files if the setting is not enabled
        if not self.settings.get("show_hidden_files", False):
            folders = [x for x in folders if not x.name.startswith(".")]
            files = [x for x in files if not x.name.startswith(".")]
        # Filter out files the user does not have read access to
        if not self.settings.get("show_permission_denied", False):
            folders = [x for x in folders if x.can_read]
            files = [x for x in files if x.can_read]

        folders.sort(key=lambda x: x.name.lower())
        files.sort(key=lambda x: x.name.lower())
        self.known_files[self.current_path] = {
            "folders": folders,
            "files": files,
            "total": len(folders) + len(files)
        }
        return folders + files

    @property
    def known_items(self):
        return self.known_files.get(self.current_path, {"folders": [], "files": []})

    @property
    def dimensions(self):
        return self.screen.getmaxyx()  # (height, width)

    def navigate(self, item: pathlib.Path):
        self.memo["preview"] = None
        navigate_to = (self.current_path / item).resolve()
        # If the user does not have read access to the item, do not navigate
        if navigate_to == self.current_path.parent.resolve():
            self.to_highlight = str(self.current_path).split("/")[-1]
        if not os.access(navigate_to, os.R_OK):
            self.memo["error"] = "Permission denied"
            return
        if os.path.isdir(navigate_to):
            self.current_path = navigate_to.resolve()
            self.selection = None
            self.search = ""
            self.search_index = 0
            self.mode = Modes.default
            self.clear()
        elif os.path.isfile(navigate_to):
            ...  # TODO

    def render(self):
        self.render_borders()

        for name, imported in self.modules.items():
            imported.callback(**self.get_externals(getattr(self.sections, name)))

    def key_hook(self, _, key, mode):  # _ is self, but it's passed in for consistency
        if mode == Modes.default:
            if key == "q" or key == Keys.escape:
                raise KeyboardInterrupt

    def handle_key(self, key):
        self.memo["error"] = None
        key = curses.keyname(key).decode("utf-8")
        for hook in self.modules.values():
            hook.key_hook(self, key, self.mode)

    def teardown(self):
        self.screen.clear()
        self.screen.refresh()
        curses.endwin()

    def resize_hook(self, force=False):
        new_dimensions = self.dimensions
        if new_dimensions != self.size_last_frame or force:
            self.memo["preview"] = None
            self.screen.clear()
            self.size_last_frame = new_dimensions

            self.sections = GridHelper(*self.dimensions, padding=True)
            self.sections.add_section("header", height=2)
            self.sections.add_section("footer", height=1, flip_align=True)
            self.sections.add_section("sidebar", width=2/5, flip_align=True)

            if self.settings.get("show_preview", True):
                self.sections.add_section("preview", within="sidebar", height=-6, flip_align=True)

            self.sections.add_remaining("main")

    def set_char(self, y, x, char, colour=0):
        try:
            self.screen.addstr(y, x, char, curses.color_pair(colour))
        except curses.error:
            pass  # This triggers when characters are written in the bottom right
    def add_text(self, y, x, text, colour=0):
        for i, char in enumerate(text):
            self.set_char(y, x + i, char, colour)
    def add_line(self, y, x, text, colour=0, panel_width=0):
        text = text[:panel_width]
        text += " " * max(0, panel_width - len(text))
        self.add_text(y, x, text, colour)

    def render_borders(self):
        highlight = self.colours.blue
        chars = {}  # (y, x): 00000 to indicate which four edges are present (top, right, bottom, left)
        # The first bit indicates if it is connected to the focused section
        for section, (height, width, top, left) in self.sections.json.items():
            colour_bit = 16 if section == self.mode_focus.get(self.mode) else 0
            for i in range(width):
                chars[(top - 1, left + i)] = chars.get((top - 1, left + i), 0) | 5 | colour_bit
                chars[(top + height, left + i)] = chars.get((top + height, left + i), 0) | 5 | colour_bit
            for i in range(height):
                chars[(top + i, left - 1)] = chars.get((top + i, left - 1), 0) | 10 | colour_bit
                chars[(top + i, left + width)] = chars.get((top + i, left + width), 0) | 10 | colour_bit
        # Draw the corners around each section
        # Firstly, set every location to 00000
        for section, (height, width, top, left) in self.sections.json.items():
            colour_bit = 16 if section == self.mode_focus.get(self.mode) else 0
            # Top left (Draw bottom and right connections)
            current = chars.get((top - 1, left - 1), 0)
            # Bitwise OR with 0110
            chars[(top - 1, left - 1)] = current | 6 | colour_bit
            # Top right
            current = chars.get((top - 1, left + width), 0)
            # Bitwise OR with 0011
            chars[(top - 1, left + width)] = current | 3 | colour_bit
            # Bottom left
            current = chars.get((top + height, left - 1), 0)
            # Bitwise OR with 1100
            chars[(top + height, left - 1)] = current | 12 | colour_bit
            # Bottom right
            current = chars.get((top + height, left + width), 0)
            # Bitwise OR with 1001
            chars[(top + height, left + width)] = current | 9 | colour_bit

        # Now, draw the corners (top, right, bottom, left)
        box_chars = {
            0: None,  # Do not draw a corner
            1: "╴",   # 0001,                  left
            2: "╷",   # 0010,           bottom
            3: "┐",   # 0011,           bottom left
            4: "╶",   # 0100,     right
            5: "─",   # 0101,     right        left
            6: "┌",   # 0110,     right bottom
            7: "┬",   # 0111,     right bottom left
            8: "╵",   # 1000, top
            9: "┘",   # 1001, top              left
            10: "│",  # 1010, top       bottom
            11: "┤",  # 1011, top       bottom left
            12: "└",  # 1100, top right
            13: "┴",  # 1101, top right        left
            14: "├",  # 1110, top right bottom
            15: "┼"   # 1111, top right bottom left
        }
        for (y, x), value in chars.items():
            char = box_chars[value & 0b1111]
            to_highlight = value & 0b10000 == 0b10000
            if char:
                self.set_char(y, x, char, highlight if to_highlight else Colours.default)

    def external_set_char(self, y_offset, x_offset):
        return lambda *args: self.set_char(args[0] + y_offset, args[1] + x_offset, args[2], len(args) > 3 and args[3] or 0)

    def external_add_text(self, y_offset, x_offset):
        return lambda *args: self.add_text(args[0] + y_offset, args[1] + x_offset, args[2], len(args) > 3 and args[3] or 0)

    def external_add_line(self, y_offset, x_offset, panel_width):
        return lambda *args: self.add_line(args[0] + y_offset, x_offset, args[1], len(args) > 2 and args[2] or 0, panel_width)

    def get_externals(self, section):
        return {
            "explorer": self,
            "height": section[0],
            "width": section[1],
            "set_char": self.external_set_char(section[2], section[3]),
            "add_text": self.external_add_text(section[2], section[3]),
            "add_line": self.external_add_line(section[2], section[3], section[1])
        }

    def render_parts(self, lines, height, width, add_line, add_text):
        for i, item in enumerate(lines[:height]):
            try:
                if isinstance(item, tuple):
                    add_line(i, item[0][:width], item[1])
                elif isinstance(item, str):
                    add_line(i, item[:width], Colours.default)
                else:
                    # Clear the line
                    add_line(i, "", Colours.default)
                    # For each part of text, render it
                    x = 0
                    for part in item:
                        if isinstance(part, str):
                            add_text(i, x, part)
                            x += len(part)
                        else:
                            add_text(i, x, part[0][:(width - x)], part[1])
                            x += len(part[0])
            except ValueError:
                add_line(i, "[Encoding error]", Colours.error)

    def clear(self):
        self.screen.clear()


def main(screen, start_path=None):
    explorer = Explorer(screen, start_path)
    try:
        renders_since_keypress = 0
        while True:
            explorer.resize_hook()

            explorer.render()
            renders_since_keypress += 1
            timeout = explorer.memo.get("refresh_interval", 10_000)
            screen.timeout(timeout if renders_since_keypress > 1 else 100)
            key = screen.getch()
            if key != -1:
                explorer.handle_key(key)
                renders_since_keypress = 0
            time.sleep(0.01)
    except KeyboardInterrupt:
        explorer.teardown()


if __name__ == "__main__":
    # Get command arguments. If -H is present, start in home directory
    args = sys.argv
    arguments = {}
    for i in range(1, len(args)):
        if args[i].startswith("-"):
            arguments[args[i]] = True
        else:
            arguments[args[i]] = args[i + 1]

    start_path = None
    if "-H" in arguments:
        start_path = pathlib.Path.home()
    else:
        # Get the current path
        start_path = pathlib.Path.cwd()
    curses.wrapper(main, start_path)
