from utils.colours import Colours
from utils.icons import Icons
import os


def get_preview_lines(file, height, width):
    try:
        file.readlines()
    except UnicodeDecodeError:
        return ["Binary file", f"Encoding: {file.encoding}"]
    if not file.encoding == "UTF-8":
        return ["Binary file", f"Encoding: {file.encoding}"]
    file.seek(0)
    lines = []
    while len(lines) <= height:
        # Read one line at a time (to avoid reading the whole file)
        line = file.readline()
        if not line:
            break
        # Remove any trailing newline characters
        line = line.rstrip()
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
    for item in os.scandir(current.location):
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
        lines.append((f" {Icons.folder.default} {item.name[:(width - 5)]}", Colours.default))
    for item in files:
        lines.append((f" {Icons.file.default} {item.name[:(width - 5)]}", Colours.default))
    available_height = height - 1
    lines = lines[:available_height]
    return [l[:width] for l in lines[:height]]


def callback(explorer, height, width, add_line, add_text, **kwargs):
    current = explorer.current_item
    lines = []
    if current.is_dir:
        lines = preview_directory(current, height, width, explorer.settings)
    elif explorer.memo.get("preview"):
        lines = explorer.memo["preview"]
    else:
        location = current.link_from or current.location
        try:
            with open(location, "r") as file:
                lines = get_preview_lines(file, height, width)
        except FileNotFoundError:
            # Broken link
            lines = [("File not found", Colours.error)]
    # Fill any blank lines
    for _ in range(height - len(lines)):
        lines.append("")

    explorer.memo["preview"] = lines

    explorer.render_parts(lines, height, width, add_line, add_text)



def key_hook(explorer, key, mode):
    ...
