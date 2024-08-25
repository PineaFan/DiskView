import os

icons = {
    "folder": {
        "default": " ",
        "parent": "󱧰 ",
        "hidden": "󰉖 ",
        "locked": "󰉐 ",
        "link": "󱧮 ",
        "hidden_link": "󱧯 "
    },
    "file": {
        "default": " ",
        "locked": "󱀰 ",
        "hidden": "󰘓 ",

        "archive": " ",
        "audio": " ",
        "binary": " ",
        "certificate": "󱆇 ",
        "configuration": "󱁻 ",
        "document": " ",
        "image": " ",
        "link": "󱅷 ",
        "lock": "󱧈 ",
        "pdf": " ",
        "video": " ",

        "cube": " ",
        "db": " ",
        "font": " ",
        "code": " ",
        "license": "󰿃 ",
        "broken_link": "󰌸 ",
    },
    "scrollbar": {
        "top": "",
        "bottom": "",
        "unfilled": " ",
        "filled": "┃"
    },
    "generic": {
        "chevron": { "right": " ", "down": " ", "up": " ", "left": " "},
        "git": "󰊢 "
    }
}

# Allow for accessing icons by doing Icons.folder.default, instead of Icons["folder"]["default"]
# This should work for whichever json is passed in, and recursively for nested dictionaries

class Icons:
    def __getattr__(self, item: str) -> any:
        return self.__getitem__(item)

    def __getitem__(self, item: str) -> any:
        return self.__dict__[item]

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __init__(self, icons: dict):
        for key, value in icons.items():
            if isinstance(value, dict):
                self.__dict__[key] = Icons(value)
            else:
                self.__dict__[key] = value

Icons = Icons(icons)


def identify_folder_icon(folder) -> str:
    if not folder.can_read:
        return Icons.folder.locked
    if folder.name == ".git":
        return Icons.generic.git
    if folder.is_parent:
        return Icons.folder.parent
    if folder.is_link:
        if folder.name.startswith("."):
            return Icons.folder.hidden_link
        return Icons.folder.link
    return Icons.folder.hidden if folder.name.startswith(".") else Icons.folder.default

def identify_file_icon(file) -> str:
    # If the current user has read access to the file
    if not file.can_read:
        return Icons.file.locked
    if file.name.startswith("."):
        return Icons.file.hidden
    extension = file.name.split(".")
    extension = extension[-1].lower()
    extensions = {
        "archive": "zip tar gz 7z rar bz2 xz".split(),
        "audio": "mp3 wav aac flac ogg wma m4a heic".split(),
        "binary": "exe bin dll iso so img dat".split(),
        "certificate": "crt pem cer pfx p12 der pub".split(),
        "configuration": "ini cfg conf json xml yml yaml toml pkl nix flake".split(),
        "document": [
            "doc", "docx", "odt", "pages",
            "rtf", "txt",
            "ppt", "pptx", "odp", "key"
            "xls", "xlsx", "numbers"
        ],
        "image": "jpg jpeg png gif bmp tif tiff webp svg qoi".split(),
        "license": "license security".split(),
        "link": "lnk url shortcut".split(),  # Also symlink
        "lock": "lock".split(),
        "pdf": "pdf epub xps cbz cbr".split(),
        "video": "mp4 avi mkv mov wmv flv webm hevc".split(),
        "cube": "mcworld mcpack mcfunction blend obj fbx stl".split(),
        "db": "db sql mdb accdb dbf sqlite3 sqlite2 sqlite".split(),
        "font": "ttf otf woff woff2 eot".split(),
        "code": "py js ts html css php cpp c h sh bat ps1 ps1xml psd1 psm1".split(),
    }
    # If it's a symlink, use the link icon
    if file.is_link:
        return Icons.file.link

    for icon, exts in extensions.items():
        if extension.lower() in exts:
            return getattr(Icons.file, icon)
    if file.name.startswith("id_"):
        return Icons.file.certificate
    if len(extension) == 1:
        return Icons.file.binary
    return Icons.file.default

def identify_icon(item):
    # File has a .is_dir attribute
    if item.is_dir:
        return identify_folder_icon(item)
    return identify_file_icon(item)
