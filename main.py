from __future__ import division

import curses

import dbgoutput
from map import Map
from tilemanager import TileManager

def main(stdscr):
    curses.curs_set(False)
    dbgoutput.init(stdscr)
    tile_m = TileManager()
    stdscr.clear()

    map = Map(curses.COLS, curses.LINES-1)
    maparray = map.get_map_array()
    for y, row in enumerate(maparray):
        for x, tile in enumerate(row):
            try:
                stdscr.addstr(y, x, tile.char, tile.color)
            except TypeError:
                raise TypeError("X:{0} Y:{1} char:{2} color:{3}".format(x, y, tile.char, tile.color))

    dbgoutput.print_output()

    stdscr.refresh()
    stdscr.getkey()


if __name__ == "__main__":
    curses.wrapper(main)
