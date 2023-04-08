from __future__ import division

import curses

import dbgoutput
from map import Map
from tilemanager import TileManager

def main(stdscr):
    #Initialize curses
    curses.curs_set(False)
    #Initialize debug output printer
    dbgoutput.init(stdscr)
    #Initialize tile manager
    tile_m = TileManager()
    #Clear the terminal
    stdscr.clear()

    #Create a new map to fill the screen. This is where the magic happens.
    map = Map(curses.COLS, curses.LINES-1)
    #Iterate over the generated map and print its contents via curses
    maparray = map.get_map_array()
    for y, row in enumerate(maparray):
        for x, tile in enumerate(row):
            try:
                stdscr.addstr(y, x, tile.char, tile.color)
            except TypeError:
                raise TypeError("X:{0} Y:{1} char:{2} color:{3}".format(x, y, tile.char, tile.color))

    #Output debugging messages in the upper-left corner
    dbgoutput.print_output()

    #Close curses and put the terminal back in normal mode.
    stdscr.refresh()
    stdscr.getkey()


if __name__ == "__main__":
    #Wrap our program in a curses scope.
    curses.wrapper(main)
    #This will clean up the terminal state if the program throws an exception,
    #or just after it finishes running.
