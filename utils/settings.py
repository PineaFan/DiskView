import platform
import json
import os
import pathlib


default_keys = {
    "linux": {
        "navigate_parent": "KEY_BACKSPACE",
        "backspace": "KEY_BACKSPACE",
        "navigate_into": "^J",
        "arrow_up": "KEY_UP",
        "arrow_down": "KEY_DOWN",
        "arrow_left": "KEY_LEFT",
        "arrow_right": "KEY_RIGHT",
        "scroll_up_page": "KEY_PPAGE",
        "scroll_down_page": "KEY_NPAGE",
        "scroll_top": "KEY_HOME",
        "scroll_bottom": "KEY_END",
        "escape": "^[",
        "delete": "KEY_DC",
        "toggle_hidden_files": "^H",
        "refresh": "^R"
    },
    "mac": {
        "navigate_parent": "^?",
        "backspace": "^?",
        "navigate_into": "^J",
        "arrow_up": "KEY_UP",
        "arrow_down": "KEY_DOWN",
        "arrow_left": "KEY_LEFT",
        "arrow_right": "KEY_RIGHT",
        "scroll_up_page": "KEY_PPAGE",
        "scroll_down_page": "KEY_NPAGE",
        "scroll_top": "KEY_HOME",
        "scroll_bottom": "KEY_END",
        "escape": "^[",
        "delete": "KEY_DC",
        "toggle_hidden_files": "^H",
        "refresh": "^R"
    },
    "about": {
        "navigate_parent": "Navigate to the parent directory",
        "backspace": "Backspace - Used to delete a character in the typing bar",
        "navigate_into": "Navigate into the selected directory, or open the selected file",
        "arrow_up": "Move the selection up",
        "arrow_down": "Move the selection down",
        "arrow_left": "Move left through the typing bar",
        "arrow_right": "Move right through the typing bar",
        "scroll_up_page": "Scroll up by 1 page",
        "scroll_down_page": "Scroll down by 1 page",
        "scroll_top": "Jump to the top of the list",
        "scroll_bottom": "Jump to the bottom of the list",
        "escape": "Close the current mode, or exit the program",
        "delete": "Deletes the character after the cursor in the typing bar",
        "toggle_hidden_files": "Toggle showing hidden files",
        "refresh": "Reload all files and directories in the current directory"
    }
}


class Keys:
    def __getattr__(self, item: str) -> any:
        return self.__getitem__(item)

    def __getitem__(self, item: str) -> any:
        if item not in self.__dict__:
            return item
        return self.__dict__[item]

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __init__(self, keys: dict):
        for key, value in keys.items():
            if isinstance(value, dict):
                self.__dict__[key] = Keys(value)
            else:
                self.__dict__[key] = value


keynames = {
    "default": {
        "navigate_parent": "Backspace",
        "backspace": "Backspace",
        "navigate_into": "Enter 󰌑 ",
        "scroll_up_page": "Page Up",
        "scroll_down_page": "Page Down",
        "scroll_top": "Home",
        "scroll_bottom": "End",
        "arrow_up": "↑",
        "arrow_down": "↓",
        "arrow_left": "←",
        "arrow_right": "→",
        "toggle_hidden_files": "^H",
    },
    "linux": {},
    "mac": {
        "scroll_up_page": "fn+↑",
        "scroll_down_page": "fn+↓",
        "scroll_top": "fn+←",
        "scroll_bottom": "fn+→"
    },
}

settings_details = {
    "show_hidden_files": ["Show hidden files", "Show files that start with a '.'"],
    "show_permission_denied": ["Show permission denied", "Show files that the user does not have permission to read"],
    "show_preview": ["Show preview", "Show the content of files and directories without opening them (May be slow, files are not executed)"],
    "use_numeric_jump": ["Use numeric jump", "Adds numbers above/below the current selection to jump to that item"],
    "cache_visited": ["Cache visited", "Cache the contents of visited directories to speed up navigation. Usually not needed"],
    "only_active_borders": ["Only active borders", "Only show a border around the active panel, instead of all panels"],
    "keymap": ["Keymap", "The keymap to use for navigation"]
}


def default_dict(original, minimum):
    for key in minimum:
        if key not in original:
            original[key] = minimum[key]
        # If the key is a dictionary, recursively check it
        elif isinstance(minimum[key], dict):
            original[key] = default_dict(original[key], minimum[key])
    return original


class Settings:
    def __init__(self):
        self.config_path = os.environ.get("XDG_CONFIG_HOME", pathlib.Path.home() / ".config")
        self.config_path = pathlib.Path(self.config_path).resolve()
        self.config_file = self.config_path / "DiskView.json"
        self.platform = platform.system().lower().replace("darwin", "mac")

        self.default_settings = {
            "show_hidden_files": False,
            "show_permission_denied": True,
            "show_preview": True,
            "use_numeric_jump": False,
            "cache_visited": False,
            "only_active_borders": False,
            "keymap": default_keys[self.platform],
        }

        # If the config file does not exist, create it
        if not self.config_file.exists():
            self.settings = self.default_settings
            self.save()
        else:
            self.settings = self.read()
            # Check their settings. If any are missing, add them
            self.settings = default_dict(self.settings, self.default_settings)
            self.save()

    def get(self, key, default=None):
        if key in self.settings:
            return self.settings[key]
        if default is not None:
            return default
        return self.default_settings[key]

    def set(self, key, value):
        key_parts = key.split(".")
        # Use a recursive function to set the value
        if len(key_parts) == 1:
            self.settings[key] = value
            self.save()
            return
        current = self.settings
        if key_parts[0] not in current:
            current[key_parts[0]] = {}
        current = current[key_parts[0]]
        self.set(".".join(key_parts[1:]), value)

    def save(self):
        self.config_file.write_text(json.dumps(self.settings, indent=4))

    def read(self):
        return json.loads(self.config_file.read_text())

    @property
    def keys(self):
        return Keys(self.settings.get("keymap", default_keys[self.platform]))

    def key_name(self, key):
        # If the key is in the keynames dictionary for that device, use that
        if key in keynames[self.platform]:
            return keynames[self.platform][key]
        elif key in keynames["default"]:
            return keynames["default"][key]
        else:
            return key

    def key_description(self, key):
        return default_keys["about"].get(key, key)
