from utils.colours import Colours
from utils.icons import Icons
from utils.structures import Item
import os
import io


def get_preview_lines(file, height, width):
    encoding_error = ["Binary file", f"Encoding: {file.encoding}"]
    if not file.encoding == "UTF-8":
        return encoding_error
    try:
        file.seek(0)
    except io.UnsupportedOperation:
        return encoding_error
    lines = []
    while len(lines) <= height:
        # Read one line at a time (to avoid reading the whole file)
        line = ""
        try:
            for _ in range(10_000):
                char = file.read(1)
                if char == "\n":
                    break
                line += char
            else:
                break
        except (UnicodeDecodeError, ValueError):
            return encoding_error
        # Truncate the line if it's too long
        line = line[:width]
        # Add the line to the list
        lines.append(line)
    return lines[:height]

def plural(amount, thing):
    amount = int(amount)
    return f"{amount} " + (thing if amount == 1 else f"{thing}s")

def preview_directory(current, height, width, settings):
    files, folders = [], []
    try:
        scan = os.scandir(current.location)
    except PermissionError:
        return [(" No read permissions", Colours.error)]
    for item in scan:
        if item.name.startswith(".") and not settings.get("show_hidden", False):
            continue
        if item.is_dir():
            folders.append(item)
        else:
            files.append(item)
    file_count, folder_count = len(files), len(folders)
    files, folders = sorted(files, key=lambda x: x.name), sorted(folders, key=lambda x: x.name)
    lines = []
    lines.append((f" {Icons.generic.total} {plural(folder_count, 'folder')}, {plural(file_count, 'file')}", Colours.accent))
    for item in folders:
        object = Item(current.location, item.name)
        if len(object.display) > width - 5:
            lines.append((f"{object.display[1:(width - 5)]}>", Colours.default))
        else:
            lines.append((f"{object.display[1:]}", Colours.default))
        if len(lines) >= height:
            break
    for item in files:
        object = Item(current.location, item.name)
        if len(object.display) > width - 5:
            lines.append((f"{object.display[1:(width - 5)]}", Colours.default))
        else:
            lines.append((f"{object.display[1:]}", Colours.default))
        if len(lines) >= height:
            break
    return lines[:height]


def callback(explorer, height, width, add_line, add_text, **kwargs):
    current = explorer.current_item
    lines = []
    if current.is_dir:
        lines = preview_directory(current, height, width, explorer.settings)
    elif not current.can_read:
        lines = [(" No read permissions", Colours.error)]
    elif explorer.memo.get("preview"):
        lines = explorer.memo["preview"]
    else:
        location = current.link_from or current.location
        try:
            with open(location, "r") as file:
                lines = get_preview_lines(file, height, width)
        except PermissionError:
            lines = [(" No read permissions", Colours.error)]
        except (FileNotFoundError, OSError):
            # Broken link
            lines = [(" File not found", Colours.error)]
    # Fill any blank lines
    for _ in range(height - len(lines)):
        lines.append("")

    explorer.memo["preview"] = lines

    explorer.render_parts(lines, height, width, add_line, add_text)



def key_hook(explorer, key, mode):
    ...
