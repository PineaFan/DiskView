from utils.colours import Colours
from utils.icons import Icons
from utils.enums import Modes
from utils.structures import Item
from utils.file_operations import rename_file


def normal_callback(explorer, height, width, add_line, add_text, **kwargs):
    lines = []

    lines.append([
        "[", (f"{Icons.generic.chevron.up}{Icons.generic.chevron.down}", Colours.accent), "| Move up/down] ",
        "[", (f"{explorer.settings.key_name('pgUp')}/{explorer.settings.key_name('pgDown')} ", Colours.accent), "| Scroll by page] ",
        "[", (f"{explorer.settings.key_name('home')}/{explorer.settings.key_name('end')} ", Colours.accent), "| Move to top/bottom] ",
    ])

    explorer.render_parts(lines, height, width, add_line, add_text)


def search_callback(explorer, height, width, add_line, add_text, **kwargs):
    lines = []

    actual_search = explorer.entry + " "
    search_characters = [c for c in actual_search]
    search_characters[explorer.entry_index] = (search_characters[explorer.entry_index], Colours.highlight)

    lines.append([
        (f"Search: ", Colours.accent),
        *search_characters,
        (f"[Press {explorer.settings.key_name('esc')} to cancel]", Colours.default)
    ])

    explorer.render_parts(lines, height, width, add_line, add_text)
    explorer.memo["refresh_interval"] = 500


def rename_callback(explorer, height, width, add_line, add_text, **kwargs):
    lines = []

    actual_name = explorer.entry + " "
    name_characters = [c for c in actual_name]

    colour = Colours.default
    dir_files = explorer.known_files.get(explorer.current_path)
    item_names = [item.name for item in dir_files["files"]] + [item.name for item in dir_files["folders"]]
    warning = ""
    if actual_name[0] == ".":
        colour = Colours.warning
        warning = (f" [File will be hidden once created]", Colours.warning)
    if actual_name[:-1] in item_names and actual_name[:-1] != explorer.current_item.name:
        colour = Colours.error
        warning = (f" [File with this name already exists]", Colours.error)
    name_characters = [(c, colour) for c in name_characters]
    name_characters[explorer.entry_index] = (name_characters[explorer.entry_index][0], Colours.highlight)

    lines.append([
        (f"Rename: ", Colours.accent),
        *name_characters,
        (f"[Press {explorer.settings.key_name('esc')} to cancel]", Colours.default),
        warning
    ])

    explorer.render_parts(lines, height, width, add_line, add_text)
    explorer.memo["refresh_interval"] = 500


def callback(explorer, **kwargs):
    if explorer.mode == Modes.default:
        normal_callback(explorer, **kwargs)
    elif explorer.mode == Modes.search:
        search_callback(explorer, **kwargs)
    elif explorer.mode == Modes.rename:
        rename_callback(explorer, **kwargs)

def key_hook(explorer, key, mode):
    if key == explorer.settings.keys.search and mode == Modes.default:
        explorer.mode = Modes.search
        explorer.regenerate_sections()

    if key == explorer.settings.keys.rename and mode == Modes.default:
        explorer.mode = Modes.rename
        explorer.entry = explorer.current_item.name
        explorer.entry_index = len(explorer.entry)
        explorer.regenerate_sections()

    if key == explorer.settings.keys.enter and mode == Modes.rename:
        name_before = explorer.current_item.name
        explorer.mode = Modes.default
        if not rename_file(explorer.current_item, explorer.entry):
            explorer.memo["error"] = f"Failed to rename {explorer.current_item.name}"
        else:
            new_item = Item(explorer.current_path, explorer.entry)
            def undo_rename():
                rename_file(new_item, name_before)
            explorer.add_undo(undo_rename)
        explorer.move_selection_to = explorer.entry
        explorer.entry = ""
        explorer.clear_cache()
        explorer.regenerate_sections()

    # Typing logic
    if mode in [Modes.search, Modes.rename]:
        # Exit search mode
        if key == explorer.settings.keys.escape:
            explorer.mode = Modes.default
            explorer.regenerate_sections()

        # Key pressed
        elif len(key) == 1:
            explorer.entry = explorer.entry[:explorer.entry_index] + key + explorer.entry[explorer.entry_index:]
            explorer.entry_index += 1

        # Character deletion
        elif key == explorer.settings.keys.backspace and explorer.entry_index > 0:
            explorer.entry = explorer.entry[:explorer.entry_index - 1] + explorer.entry[explorer.entry_index:]
            explorer.entry_index -= 1
        elif key == explorer.settings.keys.delete and explorer.entry_index < len(explorer.entry):
            explorer.entry = explorer.entry[:explorer.entry_index] + explorer.entry[explorer.entry_index + 1:]

        # Navigation
        elif key == explorer.settings.keys.arrow_right:
            explorer.entry_index = min(explorer.entry_index + 1, len(explorer.entry))
        elif key == explorer.settings.keys.arrow_left:
            explorer.entry_index = max(explorer.entry_index - 1, 0)
