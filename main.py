from __future__ import division

import random
import math
import curses

class Tile(object):
    def __init__(self, char, color=None):
        self.char = char
        self.color = color

class Map(object):
    floor = Tile('.')
    wall = Tile('#')
    impass = Tile('~')
    def init_colors(self):
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        Map.floor.color = curses.color_pair(3)
        Map.wall.color = curses.color_pair(2)
        Map.impass.color = curses.color_pair(1)

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.map_area = width * height

        self._maparray = [[Map.impass for i in range(self.width)]for j in range(self.height)]
        self.init_colors()

        self._create_map()

    def get(self, x, y):
        return self._maparray[y][x]

    def set(self, x, y, tile):
        self._maparray[y][x] = tile

    def _create_map(self):
        # num_mesas = 5
        mesa_max_radius = 6
        mesa_map_density = .02
        # for i in range(num_mesas):
        total_mesa_area = 0
        #Slop: Mesas can overlap or fall off the edge of the map.
        #We might also have a large mesa that increases mesa density past the cutoff.
        while (total_mesa_area/self.map_area) < mesa_map_density:
            x = random.randint(0, self.width-1)
            y = random.randint(0, self.height-1)
            r = random.randint(0, mesa_max_radius)
            self.make_mesa(x, y, r)
            mesa_area = r**2
            total_mesa_area += mesa_area

        for i_y, row in enumerate(self._maparray):
            for i_x, tile in enumerate(row):
                if tile == Map.floor:
                    for neighbor in get_orthog_neighbors(i_x, i_y):
                        if neighbor[0] < self.width and neighbor[1] < self.height and self.get(neighbor[0], neighbor[1]) == Map.impass:
                            self.set(neighbor[0], neighbor[1], Map.wall)

    def get_map_string(self):
        mapstring = ""
        for row in self._maparray:
            rowstring = ""
            for tile in row:
                rowstring += tile
            mapstring += rowstring
            mapstring += '\n'

    def get_map_array(self):
        return self._maparray

    def make_mesa(self, x, y, r):
        for circ_height in range(-r, r+1):
            circ_width = int(get_circle_dimensions(r, circ_height))
            for circ_x in range(x-circ_width, x+circ_width+1):
                if y+circ_height < self.height and circ_x < self.width:
                    self.set(circ_x, y+circ_height, Map.floor)


def get_circle_dimensions(r, y):
    return math.sqrt(r**2 - y**2)


def test_mesas():
    for r in range(0, 5):
        x = width/2
        y = r*(height/5) + 5
        make_mesa(x, y, r)
        map.set(x, y, '@')

def get_orthog_neighbors(x, y):
   return [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]

def main(stdscr):
    curses.curs_set(False)
    stdscr.clear()

    map = Map(curses.LINES, curses.COLS-1)
    maparray = map.get_map_array()
    for y, row in enumerate(maparray):
        for x, tile in enumerate(row):
            stdscr.addstr(x, y, tile.char, tile.color)

    stdscr.refresh()
    stdscr.getkey()


if __name__ == "__main__":
    curses.wrapper(main)
