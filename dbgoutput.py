import curses

dbg = {"debug_strings": [],
        "errorcolor": None,
        "stdscr": None}

def init(stdscr):
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    dbg["errorcolor"] = curses.color_pair(1)
    dbg["stdscr"] = stdscr


def add_string(string):
    dbg["debug_strings"].append(string)

def print_output():
    y_offset = 0
    for d_string in dbg["debug_strings"]:
        dbg["stdscr"].addstr(y_offset, 1, d_string, dbg["errorcolor"])
        y_offset += 1
    clear_output()

def clear_output():
    dbg["debug_strings"] = []
