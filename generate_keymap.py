import curses
import time
import platform
import json


class Explorer:
    def __init__(self, screen):
        self.screen = screen
        curses.curs_set(0)

    @property
    def dimensions(self):
        return self.screen.getmaxyx()  # (height, width)

    def render(self, *args):
        self.clear()
        for i in range(len(args)):
            self.add_line(i, 0, args[i], 0, self.dimensions[1])

    def handle_key(self, key):
        return curses.keyname(key).decode("utf-8")

    def teardown(self):
        self.screen.clear()
        self.screen.refresh()
        curses.endwin()

    def set_char(self, y, x, char, colour=0):
        try:
            self.screen.addstr(y, x, char, curses.color_pair(colour))
        except curses.error:
            pass

    def add_text(self, y, x, text, colour=0):
        for i, char in enumerate(text):
            self.set_char(y, x + i, char, colour)

    def add_line(self, y, x, text, colour=0, panel_width=0):
        text = text[:panel_width]
        text += " " * max(0, panel_width - len(text))
        self.add_text(y, x, text, colour)

    def wait_until_no_input(self):
        key = 1
        while key != -1:
            self.screen.timeout(100)
            key = self.screen.getch()
            time.sleep(0.01)

    def wait_for_input(self):
        key = -1
        while key == -1:
            self.screen.timeout(100)
            key = self.screen.getch()
            time.sleep(0.01)
        return self.handle_key(key)

    def clear(self):
        self.screen.clear()


def mapper(screen):
    explorer = Explorer(screen)
    try:
        device_name = platform.system().lower().replace("darwin", "mac")
        explorer.render(f"Generating keymap for: {device_name}", "Press any key to continue...")
        explorer.wait_for_input()
        explorer.wait_until_no_input()

        with open("keys.json") as f:
            raw = json.load(f)
        keys = raw[device_name]

        for key_to_modify in keys:
            explorer.render(f"Press the following key: {key_to_modify}")
            key = explorer.wait_for_input()
            explorer.render(f"Key {key_to_modify} has been set to {key}", "Loading next key...")
            keys[key_to_modify] = key
            explorer.wait_until_no_input()
        explorer.teardown()
        raw[device_name] = keys
        with open("keys.json", "w") as f:
            json.dump(raw, f, indent=4)
        print("Keymap generated successfully!")
    except KeyboardInterrupt:
        explorer.teardown()


if __name__ == "__main__":
    # Get command arguments. If -H is present, start in home directory
    curses.wrapper(mapper)
