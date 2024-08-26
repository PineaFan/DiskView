import curses

class Colours:
    default = 1
    accent = 2
    success = 3
    warning = 4
    error = 5
    info = 6

    red = 10
    green = 11
    blue = 12
    cyan = 13
    magenta = 14
    yellow = 15
    white = 16

    highlight = 20

    def __init__(self):
        curses.start_color()
        curses.init_pair(self.default, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(self.accent, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(self.success, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(self.warning, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(self.error, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(self.info, curses.COLOR_BLUE, curses.COLOR_BLACK)

        curses.init_pair(self.red, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(self.green, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(self.blue, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(self.cyan, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(self.magenta, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(self.yellow, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(self.white, curses.COLOR_WHITE, curses.COLOR_BLACK)

        curses.init_pair(self.highlight, curses.COLOR_BLACK, curses.COLOR_WHITE)


def row_highlight_colour(file, is_selected):
    if not is_selected:
        return Colours.default
    if not file.can_read:
        return Colours.error
    if file.is_parent:
        return Colours.info
    if file.name.startswith("."):
        return Colours.warning
    return Colours.accent
