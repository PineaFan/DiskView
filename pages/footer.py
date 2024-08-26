from utils.colours import Colours
from utils.icons import Icons

def callback(explorer, height, width, add_line, add_text, **kwargs):
    lines = []

    lines.append([
        (f" {Icons.generic.chevron.up}{Icons.generic.chevron.down} ", Colours.accent),
        "Move up/down"
    ])

    explorer.render_parts(lines, height, width, add_line, add_text)


def key_hook(explorer, key, mode):
    ...
