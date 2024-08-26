import pathlib
from icons import Icons
from colours import Colours
from structures import Item
from enums import Modes


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
        max_width = width - 4
        if len(name) <= max_width:
            return name
        return name[:(max_width - 1)] + " >"

    items = [] if explorer.current_path == pathlib.Path("/") else [Item(explorer.current_path, "..")]
    items += explorer.items

    # If selection is none, set it to the index of explorer.to_highlight (if it exists)
    if explorer.selection is None and explorer.to_highlight:
        # Find the item where item.name == explorer.to_highlight
        for i, item in enumerate(items):
            if item.name == explorer.to_highlight:
                explorer.selection = i
                break
    explorer.selection = explorer.selection or 0
    explorer.selection = max(min(explorer.selection, len(items) - 1), 0)
    selected_item = items[explorer.selection]

    visible = calculate_visible_range(height, explorer.selection, len(items))
    explorer.memo["visible"] = list(visible)
    # But if "parent_directory" is in the list, remove 1 from visible[1]
    if explorer.current_path != pathlib.Path("/"):
        explorer.memo["visible"][1] -= 1
    to_render = items[visible[0]:visible[1]]
    for i, item in enumerate(to_render):
        line_text = item.display

        # Add a cursor to the selected item
        if explorer.selection == i + visible[0]:
            explorer.current_item = item
            line_text = f"{Icons.generic.chevron.right}{line_text[2:]}"
        elif explorer.scroll_direction_down:
            # If this line is within the 9 after the selection
            if explorer.selection + 9 >= i + visible[0] >= explorer.selection:
                # Add relative line numbers where the cursor would be
                line_text = f"{i + visible[0] - explorer.selection} {line_text[2:]}"
        elif not explorer.scroll_direction_down:
            # If this line is within the 9 before the selection
            if explorer.selection - 9 <= i + visible[0] <= explorer.selection:
                # Add relative line numbers where the cursor would be
                line_text = f"{explorer.selection - i - visible[0]} {line_text[2:]}"

        add_line(i, restrict(line_text), item.row_colour(selected_item.location))

    is_scrollbar_needed = len(items) > height
    explorer.memo["all_on_screen"] = not is_scrollbar_needed
    if not is_scrollbar_needed:
        return
    # In the top right show Icons.scrollbar.top
    add_text(0, width - 1, Icons.scrollbar.top, Colours.accent)
    # In the bottom right show Icons.scrollbar.bottom
    add_text(height - 1, width - 1, Icons.scrollbar.bottom, Colours.accent)
    # Calculate the percentage of the list that is visible, excluding the top and bottom scrollbars
    percentage_visible = (height - 2) / len(items)
    # Calculate how big the scrollbar should be
    scrollbar_size = max(int(percentage_visible * height), 1)
    # Available starts
    available_starts = height - scrollbar_size - 1
    # Calculate the start of the scrollbar
    scrollbar_start = int(available_starts * (explorer.selection / len(items)))
    scrollbar_range = range(scrollbar_start + 1, scrollbar_start + scrollbar_size + 1)
    # Fill in the scrollbar
    for y in range(1, height - 1):
        if y in scrollbar_range:
            add_text(y, width - 1, Icons.scrollbar.filled, Colours.accent)
        else:
            add_text(y, width - 1, Icons.scrollbar.unfilled, Colours.accent)


def key_hook(explorer, key, mode):
    if mode == Modes.default:
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
            total = explorer.known_items
            total = len(total["files"]) + len(total["folders"]) + (1 if explorer.current_path != pathlib.Path("/") else 0)
            explorer.selection = total - 1
        elif key == "^J":
            selected = explorer.current_item.location
            if selected == "..":
                explorer.navigate(explorer.current_path.parent)
            else:
                explorer.navigate(explorer.current_path / selected)
        elif key == "KEY_BACKSPACE":
            if explorer.current_path != pathlib.Path("/"):
                explorer.navigate(explorer.current_path.parent)