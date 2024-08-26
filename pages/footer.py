from utils.colours import Colours
from utils.icons import Icons
from utils.keymap import key_name
from utils.enums import Modes

def callback(explorer, height, width, add_line, add_text, **kwargs):
    lines = []

    lines.append([
        "[", (f"{Icons.generic.chevron.up}{Icons.generic.chevron.down}", Colours.accent), "| Move up/down] ",
        "[", (f"{key_name('pgUp')}/{key_name('pgDown')} ", Colours.accent), "| Scroll by page] ",
        "[", (f"{key_name('home')}/{key_name('end')} ", Colours.accent), "| Move to top/bottom] ",
    ])

    explorer.render_parts(lines, height, width, add_line, add_text)


def key_hook(explorer, key, mode):
    ...
    # if key == key_name("/") and mode == Modes.default:
    #     explorer.mode = Modes.search
    # if key == key_name("esc") and mode == Modes.search:
    #     explorer.mode = Modes.default
