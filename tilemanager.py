from __future__ import division

import curses

class Tile(object):
    """Represents a tile on the map."""
    def __init__(self, char, color=None):
        self.char = char
        self.color = color

    def __str__(self):
        return self.char

class TileManager(object):
    impass = Tile('~')
    floor = Tile('.')
    wall = Tile('*')
    bridge = Tile('#')
    test_tile = Tile('@')

    def __init__(self):
        self.init_colors()

    def init_colors(self):
        """Initializes curses colors and applies them to tiles"""
        #1 is currently reserved for error messages
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
        TileManager.test_tile.color = curses.color_pair(2)
        TileManager.impass.color = curses.color_pair(2)
        TileManager.wall.color = curses.color_pair(3)
        TileManager.floor.color = curses.color_pair(4)
        TileManager.bridge.color = curses.color_pair(5)
