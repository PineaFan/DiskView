import pathlib
from colours import Colours

def callback(explorer, width, add_text, add_line, **kwargs):
    # Get the current path
    path = str(explorer.current_path)
    # Get the user's home directory
    home = str(pathlib.Path.home())
    if path.startswith(home):
        path = path.replace(home, "~", 1)
    parts = path.split("/")
    available_width = width
    add_ellipsis = False
    if len("/".join(parts)) > available_width:
        available_width -= 3  # For the "..." at the start
        add_ellipsis = True
    while len("/".join(parts)) > available_width:
        parts.pop(0)
    if add_ellipsis:
        parts.insert(0, "...")
    # Filter out ""
    parts = [part for part in parts if part]
    # For each part, render it
    x = 0
    for i, part in enumerate(parts):
        if not (i == 0 and (part == "~" or part == "...")):
            add_text(0, x, "/", Colours.default)
            x += 1
        # Render the part
        colour = Colours.default
        if part == "~":
            colour = Colours.accent
        elif i == len(parts) - 1:
            colour = Colours.accent
        elif part.startswith("."):
            colour = Colours.warning
        add_text(0, x, part, colour)
        x += len(part)
    if not parts:
        add_text(0, 0, "/", Colours.default)

    # Second line
    if explorer.memo.get("error", False):
        add_line(1, explorer.memo["error"], Colours.error)
        return
    # If all items are on screen
    current = explorer.known_files[explorer.current_path]
    if explorer.memo.get("all_on_screen", False):
        add_text(1, 0, f"Showing all {current.get('total')} items", Colours.default)
    elif current.get("total", 0) > 0:
        files_from, files_to = explorer.memo["visible"]
        add_text(1, 0, f"Showing {max(files_from, 1)} to {files_to} of {current.get('total')} items", Colours.default)
    else:
        add_text(1, 0, "No items", Colours.default)

def key_hook(explorer, key, mode):
    ...
