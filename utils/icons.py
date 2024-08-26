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
        "git": "󰊢 ",
        "total": "󰒠 ",
        "text_cursor": "󰗧 "
    },
    "languages": {
        "python": " ",
        "javascript": " ",
        "typescript": "󰛦 ",
        "react": "󰜈 ",
        "html": " ",
        "css": " ",
        "markdown": " ",
        "java": "󰬷 ",
        "c": "󰙱 ",
        "cpp": " ",
        "csharp": " ",
        "go": "󰟓 ",
        "rust": " ",
        "ruby": " ",
        "php": " ",
        "shell": " ",
        "powershell": "󰨊 ",
        "perl": " ",
        "lua": " ",
        "swift": " ",
        "kotlin": " ",
        "dart": "󰟚 ",
        "r": " ",
        "asm": " ",
        "astro": " ",
        "git": "󰊢 ",
        "docker": " ",
        "sln": "󰘐 ",
        "rss": " ",
        "vue": " ",
        "eslint": " ",
        "applescript": " ",
        "hex": "󱊧 ",
        "liquid": " ",
        "makefile": " ",
        "arduino": " "
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
        "archive": "zip tar gz 7z rar bz2 xz dmg pkg".split(),
        "audio": "mp3 wav aac flac ogg wma m4a midi".split(),
        "binary": "exe bin dll iso so img dat com".split(),
        "certificate": "crt pem cer pfx p12 der pub".split(),
        "configuration": "ini cfg conf json xml yml yaml toml pkl nix flake".split(),
        "document": [
            "doc", "docx", "odt", "pages",  # Word
            "xls", "xlsx", "numbers", "csv",  # Excel
            "ppt", "pptx", "odp", "key",  # PowerPoint
            "rtf", "txt", "readme"  # Raw text
        ],
        "image": "jpg jpeg png gif bmp tif tiff webp svg qoi psd raw heic heif ico icns".split(),
        "license": "license security".split(),
        "link": "lnk url shortcut webloc".split(),  # Also symlink
        "lock": "lock".split(),
        "pdf": "pdf epub xps cbz cbr".split(),
        "video": "mp4 avi mkv mov wmv flv webm hevc mpg".split(),
        "cube": "mcworld mcpack mcfunction blend obj fbx stl ply mcmeta".split(),
        "db": "db sql mdb accdb dbf sqlite3 sqlite2 sqlite".split(),
        "font": "ttf otf woff woff2 eot".split()
    }
    languages = {
        "python": "py pyw pyc".split(),
        "javascript": "js es6".split(),
        "typescript": "ts tsconfig".split(),
        "react": "jsx tsx".split(),
        "html": "html htm xhtml".split(),
        "css": "css scss sass less".split(),
        "markdown": "md markdown".split(),
        "java": "java class jar".split(),
        "c": "c h".split(),
        "cpp": "cpp hpp cc hh cxx hxx c++ h++".split(),
        "csharp": "cs".split(),
        "go": "go".split(),
        "rust": "rs".split(),
        "ruby": "rb".split(),
        "php": "php phar".split(),
        "shell": "sh bash zsh fish command bat cmd".split(),
        "powershell": "ps1 psd1 psm1".split(),
        "perl": "pl pm".split(),
        "lua": "lua".split(),
        "swift": "swift".split(),
        "kotlin": "kt".split(),
        "dart": "dart".split(),
        "r": "r".split(),
        "asm": "asm s".split(),
        "astro": "astro".split(),
        "git": "gitignore gitattributes".split(),
        "docker": "dockerfile".split(),
        "sln": "sln".split(), # Visual Studio Solution
        "rss": "rss".split(),
        "vue": "vue".split(),
        "eslint": "eslint eslintrc eslintignore".split(),
        "applescript": "scpt".split(),
        "hex": "hex".split(),
        "liquid": "liquid".split(),
        "makefile": "makefile".split(),
        "arduino": "ino".split()
    }
    # If it's a symlink, use the link icon
    if file.is_link:
        return Icons.file.link

    for icon, exts in languages.items():
        if extension.lower() in exts:
            return getattr(Icons.languages, icon)
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
