from utils.colours import Colours


def get_preview_lines(file, height, width):
    try:
        file.readlines()
    except UnicodeDecodeError:
        return ["Binary file", f"Encoding: {file.encoding}"]
    if not file.encoding == "UTF-8":
        return ["Binary file", f"Encoding: {file.encoding}"]
    file.seek(0)
    lines = [""]
    max_chars = height * width * 5
    read = 0
    while len(lines) <= height:
        # Read one character at a time
        char = file.read(1)
        if not char:
            break
        if char == "\n":
            lines.append("")
        else:
            lines[-1] += char
        if len(lines[-1]) >= width:
            # Ignore the rest of the line, find the next newline
            while char != "\n":
                read += 1
                if read > max_chars:
                    lines.append("...")
                    break
                char = file.read(1)
    return lines[:height]


def callback(explorer, height, width, add_line, add_text, **kwargs):
    current = explorer.current_item
    lines = []
    if current.is_dir:
        lines = ["Directory"]
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
