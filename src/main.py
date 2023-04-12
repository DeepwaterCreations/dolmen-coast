#!/usr/bin/env python3

import sys
import curses

import dbgoutput
import keyinput
import events
from gamemap import Gamemap
from tilemanager import TileManager
from screenpanels import MessagePanel, ListMenu, GamePanel

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

    gamepanel, panellist = create_panel_layout(stdscr)

    #Output debugging messages in the upper-left corner
    dbgoutput.print_output()

    #Game Loop
    while True:
        try:
            draw_screen(stdscr, gamemap, gamepanel, panellist, show_debug_text=True)
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

def draw_screen(stdscr, gamemap, gamepanel, panellist, show_debug_text=False):
    #Update panels
    for panel in panellist:
        panel.display()

    gamepanel.display(gamemap.get_map_array())

    if show_debug_text:
        dbgoutput.print_output()

def create_panel_layout(stdscr):
    """Returns a tuple:
    First, the game window.
    Second, a list of other game panels
    These are all sub-windows of stdscr.
    """
    screen_width = curses.COLS-1
    screen_height = curses.LINES-1

    MESSAGEPANEL_HEIGHT = 5
    gamepanel_width = 3 * (screen_width // 4)

    #Args are height, width, top, left
    messagepanel = MessagePanel(stdscr.subwin(MESSAGEPANEL_HEIGHT, gamepanel_width, 0, 0))
    gamepanel = GamePanel(stdscr.subwin(screen_height - MESSAGEPANEL_HEIGHT, gamepanel_width, MESSAGEPANEL_HEIGHT + 1, 0))
    menupanel = ListMenu(stdscr.subwin(screen_height, (screen_width // 4), 0, gamepanel_width + 1))

    return (gamepanel, [messagepanel, menupanel])



if __name__ == "__main__":
    #Wrap our program in a curses scope.
    curses.wrapper(main)
    #This will clean up the terminal state if the program throws an exception,
    #or just after it finishes running.
