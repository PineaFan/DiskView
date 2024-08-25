from colours import Colours


def int_to_rwx(permissions):
    rwx = ""
    # Permissions is an integer with 3 digits
    digits = str(permissions)
    for permission in digits:
        permission = int(permission)
        rwx += "r" if permission >= 4 else "-"
        rwx += "w" if permission % 4 >= 2 else "-"
        rwx += "x" if permission % 2 >= 1 else "-"
    return rwx


def callback(explorer, height, width, add_line, **kwargs):
    current = explorer.current_item
    name_width = width - 5  # Padding + icon
    file_name = current.name
    # Split the name into chunks of name_width
    chunks = [file_name[i:i + name_width] for i in range(0, len(file_name), name_width)]

    lines = []  # Tuples of (line, text)
    lines.append((f" {current.icon} {chunks[0]}", Colours.accent))
    if len(chunks) > 1:
        for chunk in chunks[1:]:
            lines.append((f"    {chunk}", Colours.accent))

    u_rwx = int_to_rwx(current.permissions[0])
    g_rwx = int_to_rwx(current.permissions[1])
    a_rwx = int_to_rwx(current.permissions[2])
    character = "l" if current.is_link else "d" if current.is_dir else "."
    lines.append((f" {character}/{u_rwx}/{g_rwx}/{a_rwx}", Colours.default))
    lines.append((f" Owner: {current.owner} | Group: {current.group}", Colours.default))

    for i, (line, colour) in enumerate(lines):
        add_line(i, line, colour)



def key_hook(explorer, key):
    ...
