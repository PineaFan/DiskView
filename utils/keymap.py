import platform
import json


class Keys:
    def __getattr__(self, item: str) -> any:
        return self.__getitem__(item)

    def __getitem__(self, item: str) -> any:
        if item not in self.__dict__:
            return item
        return self.__dict__[item]

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __init__(self, icons: dict):
        for key, value in icons.items():
            if isinstance(value, dict):
                self.__dict__[key] = Keys(value)
            else:
                self.__dict__[key] = value


keynames = {
    "default": {
        "pgUp": "Page Up",
        "pgDown": "Page Down",
        "home": "Home",
        "end": "End",
        "up": "↑",
        "down": "↓",
        "left": "←",
        "right": "→",
    },
    "mac": {
        "pgUp": "fn+↑",
        "pgDown": "fn+↓",
        "home": "fn+←",
        "end": "fn+→"
    },
}


with open("keys.json") as f:
    keys = json.load(f)

# Get if the user is on "linux", "mac" or "windows"
device = platform.system().lower().replace("darwin", "mac")

Keys = Keys(keys.get(device, {}))

def key_name(key):
    # If the key is in the keynames dictionary for that device, use that
    if key in keynames.get(device, {}):
        return keynames[device][key]
    elif key in keynames["default"]:
        return keynames["default"][key]
    else:
        return key
