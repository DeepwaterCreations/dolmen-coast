import curses

class DebugOutput(object):

    def __init__(self, stdscr):
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        self.errorcolor = curses.color_pair(1)
        self.debug_strings = []
        self.stdscr = stdscr

    def add_string(self, string):
        self.debug_strings.append(string)

    def print_output(self, stdscr):
        y_offset = 0
        for d_string in self.debug_strings:
            self.stdscr.addstr(y_offset, 1, d_string, self.errorcolor)
            y_offset += 1

    def clear_output(self):
        self.debug_strings = []

