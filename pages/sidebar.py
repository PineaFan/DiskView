from utils.colours import Colours
import datetime


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


def plural(amount, thing):
    amount = int(amount)
    return f"{amount} " + (thing if amount == 1 else f"{thing}s")

def delta_duration(seconds):  # Seconds
    if seconds < 60:
        return plural(seconds, "second")
    minutes = seconds / 60
    if minutes < 60:
        return plural(minutes, "minute")
    hours = minutes / 60
    if hours < 24:
        return plural(hours, "hour")
    days = hours / 24
    if days < 7:
        return plural(days, "day")
    weeks = days / 7
    if weeks < 4:
        return plural(weeks, "week")
    months = days / 30
    if months < 12:
        return plural(months, "month")
    years = days / 365
    return plural(years, "year")


def format_time(date: float):
    date = datetime.datetime.fromtimestamp(date)
    return date.strftime("%Y-%m-%d %H:%M")

def screen_refresh_interval(modified_date: float):
    seconds = datetime.datetime.now().timestamp() - modified_date
    groups = [60, 60, 24, 7, 30, 12]
    # For each group, if multiplying all previous groups is less than the current seconds, divide by the group
    for i, group in enumerate(groups):
        if seconds / (group ** i) < 1:
            return int(seconds)
        seconds /= group ** i
    return int(seconds)


def callback(explorer, height, width, add_line, add_text, **kwargs):
    current = explorer.current_item
    name_width = width - 4  # Padding + icon
    file_name = current.name

    lines = []  # List of lists of (text, colour) or (text, colour)
    lines.append((f" {current.icon} {file_name[:name_width]}", Colours.accent))
    if current.is_link and current.link_from:
        if current.link_from.startswith(f"/home/{explorer.username}"):
            lines.append((f" -> ~/{current.link_from.split('/')[-1]}", Colours.warning))
        else:
            lines.append((f" -> {current.link_from}", Colours.warning))

    u_rwx = int_to_rwx(current.permissions[0])
    g_rwx = int_to_rwx(current.permissions[1])
    a_rwx = int_to_rwx(current.permissions[2])
    character = "l" if current.is_link else "d" if current.is_dir else "."
    lines.append([
        f" {character}/",
        (f"{u_rwx}", Colours.success), f"/",
        (f"{g_rwx}", Colours.warning), f"/",
        (f"{a_rwx}", Colours.error)
    ])
    lines.append([
        f" Owner: ",
        (current.owner, Colours.success),
        f" | Group: ",
        (current.group, Colours.warning)
    ])


    lines.append([
        (" M: ", Colours.default),
        (format_time(current.modified), Colours.accent),
        (" (" + delta_duration(datetime.datetime.now().timestamp() - current.modified) + " ago)", Colours.default)
    ])
    if current.size:
        # Calculate the size in human-readable format
        bytes = current.size
        units = [("KB", "KiB"), ("MB", "MiB"), ("GB", "GiB"), ("TB", "TiB")]
        unit = 0
        kb, kib = bytes / 1000, bytes / 1024
        while kb > 1_000:
            unit += 1
            kb /= 1000
            kib /= 1024
        lines.append([
            (" Size: ", Colours.default),
            (f"{kb:.2f} {units[unit][0]}", Colours.accent),
            (f" ({kib:.2f} {units[unit][1]}, {bytes:,} bytes)", Colours.default)
        ])
    # Shortest duration will be modified.
    explorer.memo["refresh_interval"] = screen_refresh_interval(current.modified)

    explorer.render_parts(lines, height, width, add_line, add_text)


def key_hook(explorer, key, mode):
    ...
