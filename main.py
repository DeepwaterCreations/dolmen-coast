from __future__ import division

import random
import math
import curses

class Tile(object):
    def __init__(self, char, color=None):
        self.char = char
        self.color = color

class Mesa(object):

    def __init__(self, x, y, r):
        #x,y are the origin-tile in the upper-left corner.
        self.x = x
        self.y = y
        self.center_x = self.x + r
        self.center_y = self.y + r

        self.r = r
        self.width = (2*r)+1
        self.height = (2*r)+1
        self._patch = [[None for i in range(self.width)]for j in range(self.height)]

        #Create the mesa, treating the center tile as the origin.
        for circ_height in range(-self.r, self.r+1):
            rib_width = int(self._get_ribwidth_from_height(circ_height))
            for circ_x in range(-rib_width, rib_width+1):
                self._patch[circ_height+r][circ_x+r] = Map.floor

    def get(self, x, y):
        return self._patch[y][x]

    def set(self, x, y, tile):
        self._patch[y][x] = tile
         
    def _get_ribwidth_from_height(self, y_offset):
        """Returns the horizontal distance from a vertical line through the center to the 
        edge of the circle at a given vertical offset from its center
        """
        return math.sqrt(self.r**2 - y_offset**2)

class Map(object):
    impass = Tile('~')
    floor = Tile('.')
    wall = Tile('#')
    test_tile = Tile('@')
    def init_colors(self):
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        Map.floor.color = curses.color_pair(3)
        Map.wall.color = curses.color_pair(2)
        Map.impass.color = curses.color_pair(1)
        Map.test_tile.color = curses.color_pair(1)

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.map_area = width * height

        self._maparray = [[Map.impass for i in range(self.width)]for j in range(self.height)]
        self._mesas = []
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
            r = random.randint(0, mesa_max_radius)
            x = random.randint(0, self.width-(2*r + 1))
            y = random.randint(0, self.height-r)
            self.make_mesa(x, y, r)
            mesa_area = r**2
            total_mesa_area += mesa_area
        # self.test_mesas()

        #Add walls around the mesas
        for i_y, row in enumerate(self._maparray):
            for i_x, tile in enumerate(row):
                if tile == Map.floor:
                    for neighbor in get_orthog_neighbors(i_x, i_y):
                        if neighbor[0] < self.width and neighbor[1] < self.height and self.get(neighbor[0], neighbor[1]) == Map.impass:
                            self.set(neighbor[0], neighbor[1], Map.wall)
    def test_mesas(self):
        for r in range(0, 5):
            x = self.width//2
            y = r*(self.height//5) + 5
            self.make_mesa(x-r, y-r, r)
            self.set(x, y, Map.test_tile)

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
        new_mesa = Mesa(x, y, r)
        self._mesas.append(new_mesa)
        self.apply_patch(new_mesa)

    def apply_patch(self, patchsource):
        patch = patchsource._patch
        for i_y, row in enumerate(patch):
            for i_x, tile in enumerate(row):
                if tile != None:
                    self.set(i_x + patchsource.x, i_y + patchsource.y, tile)
        

def get_orthog_neighbors(x, y):
   return [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]

def main(stdscr):
    curses.curs_set(False)
    stdscr.clear()

    map = Map(curses.LINES, curses.COLS-1)
    map.init_colors()
    maparray = map.get_map_array()
    for y, row in enumerate(maparray):
        for x, tile in enumerate(row):
            stdscr.addstr(x, y, tile.char, tile.color)

    stdscr.refresh()
    stdscr.getkey()


if __name__ == "__main__":
    curses.wrapper(main)
