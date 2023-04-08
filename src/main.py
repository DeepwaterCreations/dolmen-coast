#!/usr/bin/env python3

import sys
import curses

import dbgoutput
import keyinput
import events
from gamemap import Gamemap
from tilemanager import TileManager

def main(stdscr):
    #Initialize curses
    curses.curs_set(False) #Turn off the cursor
    #Initialize debug output printer
    dbgoutput.init(stdscr)
    #Initialize tile manager
    tile_m = TileManager()
    #Clear the terminal
    stdscr.clear()

    #Create a new map to fill the screen.
    gamemap = Gamemap(curses.COLS, curses.LINES-1)

    #Output debugging messages in the upper-left corner
    dbgoutput.print_output()

    #Game Loop
    while True:
        try:
            draw_screen(stdscr, gamemap, show_debug_text=True)
            keyinput.handle_key(stdscr.getkey())
            # gameworld.update_world()
        except KeyboardInterrupt:
            #Ctrl-C
            stdscr.refresh()
            sys.exit()
        except SystemExit:
            stdscr.refresh()
            sys.exit()

    #Close curses and put the terminal back in normal mode.
    stdscr.refresh()
    stdscr.getkey()

def draw_screen(stdscr, gamemap, show_debug_text=False):
    #Iterate over the generated map and print its contents via curses
    maparray = gamemap.get_map_array()
    for y, row in enumerate(maparray):
        for x, tile in enumerate(row):
            try:
                stdscr.addstr(y, x, tile.char, tile.color)
            except TypeError:
                raise TypeError("X:{0} Y:{1} char:{2} color:{3}".format(x, y, tile.char, tile.color))
    if show_debug_text:
        dbgoutput.print_output()



if __name__ == "__main__":
    #Wrap our program in a curses scope.
    curses.wrapper(main)
    #This will clean up the terminal state if the program throws an exception,
    #or just after it finishes running.
