import curses

class Colours:
    default = 2**0
    accent = 2**1
    success = 2**2
    warning = 2**3
    error = 2**4

    def __init__(self):
        curses.start_color()
        curses.init_pair(self.default, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(self.accent, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(self.success, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(self.warning, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(self.error, curses.COLOR_RED, curses.COLOR_BLACK)


def row_highlight_colour(file, is_selected):
    if not is_selected:
        return Colours.default
    if not file.can_read:
        return Colours.error
    if file.name.startswith(".") or file.is_parent:
        return Colours.warning
    return Colours.accent
