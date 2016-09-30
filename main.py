from __future__ import division

import random
import math
import curses

import dbgoutput

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
        TileManager.floor.color = curses.color_pair(4)
        TileManager.wall.color = curses.color_pair(3)
        TileManager.impass.color = curses.color_pair(2)
        TileManager.test_tile.color = curses.color_pair(2)

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
            rib_width = int(self.get_ribwidth(circ_height))
            for circ_x in range(-rib_width, rib_width+1):
                self.set(circ_x+r, circ_height+r, TileManager.floor)

    def get(self, x, y):
        return self._patch[y][x]

    def set(self, x, y, tile):
        self._patch[y][x] = tile
         
    def get_ribwidth(self, offset):
        """Returns the perpendicular distance to the edge of the circle from a line
        through the center of the circle at a given offset.
        """
        return math.sqrt(self.r**2 - offset**2)

    def __str__(self):
        patchstring = ""
        for row in self._patch:
            rowstring = ""
            for tile in row:
                if tile != None:
                    rowstring += tile.char
                else:
                    rowstring += ' '
            patchstring += rowstring
            patchstring += '\n'
        return patchstring

class Bridge(object):

    def __init__(self, x, y, length, direction):
        self.x = x
        self.y = y

        self.length = length

        self._patch = [[]]
        self.width = 0
        self.height = 0
        self._build_bridge(direction)

    def _build_bridge(self, direction):
        self.width = min(abs(self.length * direction[0]), 1)
        self.height = min(abs(self.length * direction[1]), 1)
        self._patch = [[None for i in range(self.width)]for j in range(self.height)]
        for patch_x, patch_y in range(length):
            patch[patch_y * direction[1]][patch_x * direction[0]] = TileManager.bridge


class Map(object):

    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.map_area = height * width

        self._maparray = [[TileManager.impass for i in range(self.height)]for j in range(self.width)]
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
            x = random.randint(0, self.height-(2*r + 1))
            y = random.randint(0, self.width-(2*r + 1))
            self.make_mesa(x, y, r)
            mesa_area = r**2
            total_mesa_area += mesa_area
        # self.test_mesas()

        #Add walls around the mesas
        for i_y, row in enumerate(self._maparray):
            for i_x, tile in enumerate(row):
                if tile == TileManager.floor:
                    for neighbor in get_orthog_neighbors(i_x, i_y):
                        if neighbor[0] < self.height and neighbor[1] < self.width and self.get(neighbor[0], neighbor[1]) == TileManager.impass:
                            self.set(neighbor[0], neighbor[1], TileManager.wall)

    def _check_overlap(self, box1, box2):
        """Returns a tuple containing whether the boxes have horizontal and vertical overlap.
        They have overlap if you can draw a staight, orthogonal line from one to the other and touch a point
        on each. Horizontal overlap means they are horizontally colinear, vertical overlap means they are 
        vertically colinear.
        """
        h_overlap = False
        v_overlap = False
        box1_bottom = box1.y + box1.height
        box2_bottom = box2.y + box2.height
        box1_right = box1.x + box1.width
        box2_right = box2.x + box2.width
        h_overlap = (box1.y < box2.y < box1_bottom or 
                    box2.y < box1.y < box2_bottom)
        v_overlap = (box1.x < box2.x < box1_right or 
                    box2.x < box1.x < box2_right)
        return (h_overlap, v_overlap)

    def _check_collision(self, box1, box2):
        """Returns true if boxes share the same space"""
        h_overlap, v_overlap = self._check_overlap(box1, box2)
        return h_overlap and v_overlap


    def test_mesas(self):
        """Generates 5 mesas in a column, descending in size."""
        for r in range(0, 5):
            x = self.height//2
            y = r*(self.width//5) + 5
            self.make_mesa(x-r, y-r, r)
            self.set(x, y, TileManager.test_tile)

    def get_map_array(self):
        return self._maparray

    def make_mesa(self, x, y, r):
        """Generates a new mesa with radius r and adds it to the map with its top-left corner at x,y"""
        new_mesa = Mesa(x, y, r)
        self._mesas.append(new_mesa)
        self.apply_patch(new_mesa)

    def apply_patch(self, patchsource):
        """Adds a set of tiles to the map from an object that has a patch and a set of x,y coordinates"""
        patch = patchsource._patch
        for i_y, row in enumerate(patch):
            for i_x, tile in enumerate(row):
                if tile != None:
                    self.set(i_x + patchsource.x, i_y + patchsource.y, tile)

    def __str__(self):
        mapstring = ""
        for row in self._maparray:
            rowstring = ""
            for tile in row:
                rowstring += tile.char
            mapstring += rowstring
            mapstring += '\n'
        return mapstring

        

def get_orthog_neighbors(x, y):
    """For the given x,y coordinates, returns a list of tuples
    containing adjacent coordinates to the left, right, up and down
    """
    return [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]


def main(stdscr):
    curses.curs_set(False)
    dbgoutput.init(stdscr)
    tile_m = TileManager()
    stdscr.clear()

    map = Map(curses.COLS-1, curses.LINES)
    maparray = map.get_map_array()
    for y, row in enumerate(maparray):
        for x, tile in enumerate(row):
            stdscr.addstr(x, y, tile.char, tile.color)

    dbgoutput.print_output()

    stdscr.refresh()
    stdscr.getkey()


if __name__ == "__main__":
    curses.wrapper(main)
