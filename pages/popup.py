from utils.colours import Colours
from utils.icons import Icons


def callback(explorer, height, width, add_line, add_text, **kwargs):
    lines = []
    # Split the title into words
    title_words = explorer.popup.title.split(" ")
    current_width = 0
    lines.append("")
    for word in title_words:
        # If the word is too long to fit on the current line
        if current_width + len(word) > width:
            lines.append("")
            current_width = 0
        # Add the word to the current line
        lines[-1] += word + " "
        current_width += len(word) + 1
    lines = [(t, Colours.error) for t in lines]
    # If there are no lines, add an empty line
    if not lines:
        lines.append("")
    lines.append("")
    description_lines = explorer.popup.description.split("\n")
    for line in description_lines:
        lines.append("")
        description_words = line.split(" ")
        current_width = 0
        for word in description_words:
            if current_width + len(word) > width:
                lines.append("")
                current_width = 0
            lines[-1] += word + " "
            current_width += len(word) + 1
        if not lines:
            lines.append("")
    lines.append("")

    options = explorer.popup.options  # List of {text: str, callback: Callable}
    option_length = sum([len(option["text"]) + 4 for option in options]) + len(options) - 1
    option_start = (width - option_length) // 2
    line = [" " * option_start]
    for i, option in enumerate(options):
        icon = Icons.generic.chevron.right if i == explorer.selection else "  "
        colour = Colours.accent if i == explorer.selection else Colours.default
        line.append((f" [{icon}{option['text']}]", colour))
    lines.append(line)

    # Center all the lines:
    for i, line in enumerate(lines):
        if type(line) == str:
            lines[i] = center(width, line)
        elif type(line) == tuple:
            lines[i] = (center(width, line[0]), line[1])

    explorer.render_parts(lines, height, width, add_line, add_text)


def center(width, text):
    return " " * ((width - len(text)) // 2) + text


def key_hook(explorer, key, mode):
    if key == explorer.settings.keys.escape:
        explorer.mode = explorer.popup.mode_on_close
        explorer.selection = explorer.popup.retain_selection
        explorer.popup = None
    if key == explorer.settings.keys.enter:
        out =  explorer.popup.options[explorer.selection]["callback"]
        explorer.selection = explorer.popup.retain_selection
        return out
    if key == explorer.settings.keys.arrow_left:
        explorer.selection = max(0, explorer.selection - 1)
    if key == explorer.settings.keys.arrow_right:
        explorer.selection = min(len(explorer.popup.options) - 1, explorer.selection + 1)
    explorer.render()
