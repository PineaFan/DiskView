from utils.colours import Colours
from utils.icons import Icons
from utils.keymap import Keys, key_name
from utils.enums import Modes
import datetime


def normal_callback(explorer, height, width, add_line, add_text, **kwargs):
    lines = []

    lines.append([
        "[", (f"{Icons.generic.chevron.up}{Icons.generic.chevron.down}", Colours.accent), "| Move up/down] ",
        "[", (f"{key_name('pgUp')}/{key_name('pgDown')} ", Colours.accent), "| Scroll by page] ",
        "[", (f"{key_name('home')}/{key_name('end')} ", Colours.accent), "| Move to top/bottom] ",
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
        (f"[Press {key_name('esc')} to cancel]", Colours.default)
    ])

    explorer.render_parts(lines, height, width, add_line, add_text)
    explorer.memo["refresh_interval"] = 500


def callback(explorer, **kwargs):
    if explorer.mode == Modes.default:
        normal_callback(explorer, **kwargs)
    elif explorer.mode == Modes.search:
        search_callback(explorer, **kwargs)

def key_hook(explorer, key, mode):
    if key == Keys["/"] and mode == Modes.default:
        explorer.mode = Modes.search
        explorer.regenerate_sections()
    if key == Keys.escape and mode == Modes.search:
        explorer.mode = Modes.default
        explorer.regenerate_sections()
    elif mode == Modes.search and len(key) == 1:
        explorer.entry = explorer.entry[:explorer.entry_index] + key + explorer.entry[explorer.entry_index:]
        explorer.entry_index += 1
    elif mode == Modes.search and key == Keys.backspace and explorer.entry_index > 0:
        explorer.entry = explorer.entry[:explorer.entry_index - 1] + explorer.entry[explorer.entry_index:]
        explorer.entry_index -= 1
    elif mode == Modes.search and key == Keys.arrow_right:
        explorer.entry_index = min(explorer.entry_index + 1, len(explorer.entry))
    elif mode == Modes.search and key == Keys.arrow_left:
        explorer.entry_index = max(explorer.entry_index - 1, 0)
    elif mode == Modes.search and key == Keys.delete and explorer.entry_index < len(explorer.entry):
        explorer.entry = explorer.entry[:explorer.entry_index] + explorer.entry[explorer.entry_index + 1:]
