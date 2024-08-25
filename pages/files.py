import os
import pathlib
from icons import Icons, identify_folder_icon, identify_file_icon
from colours import Colours, row_highlight_colour
from structures import Item

def calculate_visible_range(height, selection, total):
    if total <= height:
        return 0, total
    half = height // 2
    if selection < half:
        return 0, height
    if selection + half + 1 > total:
        return total - height, total
    return selection - half, selection + (height - half)


def callback(explorer, height, width, add_line, add_text, **kwargs):
    # restrict = lambda name: name[:(width - 8)]  # Width, icon, space around icon, scrollbar
    def restrict(name: str) -> str:
        max_width = width - 8
        if len(name) <= max_width:
            return name
        return name[:(max_width - 1)] + " >"

    items = [] if explorer.current_path == pathlib.Path("/") else [Item(explorer.current_path, "..")]
    items += explorer.items

    explorer.selection = min(explorer.selection, len(items) - 1)
    selected_item = items[explorer.selection]

    visible = calculate_visible_range(height, explorer.selection, len(items))
    to_render = items[visible[0]:visible[1]]
    for i, item in enumerate(to_render):
        line_text = item.display
        if explorer.selection == i + visible[0]:
            explorer.current_item = item.location
            line_text = f"{Icons.generic.chevron.right}{line_text[2:]}"
        add_line(i, restrict(line_text), item.row_colour(selected_item.location))


def key_hook(explorer, key):
    if key == "KEY_UP":
        explorer.selection -= 1
    elif key == "KEY_DOWN":
        explorer.selection += 1
    elif key == "KEY_PPAGE":
        # Change selection by the height of the "main" panel
        explorer.selection -= explorer.sections.main[0]
    elif key == "KEY_NPAGE":
        explorer.selection += explorer.sections.main[0]
    elif key == "KEY_HOME":
        explorer.selection = 0
    elif key == "KEY_END":
        total = explorer.known_items + (1 if explorer.current_path != pathlib.Path("/") else 0)
        total = len(total["files"]) + len(total["folders"])
        explorer.selection = total - 1
    elif key == "^J":
        selected = explorer.current_item
        if selected == "..":
            explorer.navigate(explorer.current_path.parent)
        else:
            explorer.navigate(explorer.current_path / selected)
        explorer.selection = 0
    elif key == "KEY_BACKSPACE":
        if explorer.current_path != pathlib.Path("/"):
            explorer.navigate(explorer.current_path.parent)
        explorer.selection = 0
    explorer.selection = max(0, min(explorer.selection, len(explorer.items)))
