import pathlib
import itertools
from utils.colours import Colours

def callback(explorer, height, width, add_text, add_line, **kwargs):
    # Get the current path
    path = explorer.current_path.absolute()
    cwd = pathlib.Path("/")
    parts = []
    for part in path.parts[1:]:
        cwd /= part
        colour = Colours.default
        if cwd == path:
            colour = Colours.accent
        elif cwd.is_symlink():
            colour = Colours.magenta
        elif part.startswith("."):
            colour = Colours.warning
        parts.append((part, colour))
    if len(parts) >= 2 and parts[0][0] == "home" and parts[1][0] == explorer.username:
        parts = [("~", Colours.accent)] + parts[2:]
    else:
        parts = [""] + parts
    if path == pathlib.Path("/"):
        parts = [("/", Colours.accent)]
    add_ellipsis = False
    if add_ellipsis:
        parts = ["..."] + parts
    parts = list(itertools.chain(*[[x, "/"] for x in parts]))[:-1]
    # explorer.add_text(0, 0, str(parts))
    explorer.render_parts([parts], height, width, add_line, add_text)

    # Second line
    if explorer.memo.get("error", False):
        add_line(1, explorer.memo["error"], Colours.error)
        return
    if explorer.memo.get("info", False):
        add_line(1, explorer.memo["info"], Colours.accent)
        return
    # If all items are on screen
    current = explorer.known_files[explorer.current_path]
    info = f" ({len(current.get('folders', 0))} folders, {len(current.get('files', 0))} files)"
    if explorer.memo.get("all_on_screen", False):
        add_line(1, f"Showing all {current.get('total')} items" + info, Colours.default)
    elif current.get("total", 0) > 0:
        files_from, files_to = explorer.memo["visible"]
        add_line(1, f"Showing {max(files_from, 1)} to {files_to} of {current.get('total')} items" + info, Colours.default)
    else:
        add_line(1, "No items", Colours.default)

def key_hook(explorer, key, mode):
    ...
