from __future__ import division

import random
import math

from patches import Mesa, Bridge
from tilemanager import TileManager

class Map(object):

    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.map_area = height * width

        self._maparray = [[TileManager.impass for i in range(self.width)]for j in range(self.height)]
        self._mesas = []
        self._bridges = []
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
            y = random.randint(0, self.height-(2*r + 1))
            x = random.randint(0, self.width-(2*r + 1))
            self.make_mesa(x, y, r)
            mesa_area = r**2
            total_mesa_area += mesa_area
        # self.test_mesas()

        #Add walls around the mesas
        for i_y, row in enumerate(self._maparray):
            for i_x, tile in enumerate(row):
                if tile == TileManager.floor:
                    for neighbor in get_orthog_neighbors(i_x, i_y):
                        if neighbor[0] < self.width and neighbor[1] < self.height and self.get(neighbor[0], neighbor[1]) == TileManager.impass:
                            self.set(neighbor[0], neighbor[1], TileManager.wall)

        #Build bridges between mesas
        #For each pair of mesas, get the set of unchecked mesas that are colinear.
        #Trim this list to the closest neighbor in each direction.
        #Then, for each neighbor, probabilistically build a bridge or don't.
        for checked_idx, mesa in enumerate(self._mesas):
            closest_mesas = {'N':None, 'E':None, 'S':None, 'W':None}
            for mesa2 in self._mesas[checked_idx+1:]:
                h_overlap, v_overlap =  self._check_overlap(mesa, mesa2)
                if self._check_collision(mesa, mesa2):
                    continue
                if h_overlap:
                    relative = mesa2.x - mesa.x
                    dir = 'E' if relative > 0 else 'W'
                    distance = abs(relative)
                    if closest_mesas[dir] != None:
                        prev_distance = abs(closest_mesas[dir].x - mesa.x)
                        if distance < prev_distance:
                            closest_mesas[dir] = mesa2
                    else:
                        closest_mesas[dir] = mesa2
                if v_overlap:
                    relative = mesa2.y - mesa.y
                    dir = 'N' if relative > 0 else 'S'
                    distance = abs(relative)
                    if closest_mesas[dir] != None:
                        prev_distance = abs(closest_mesas[dir].y - mesa.y)
                        if distance < prev_distance:
                            closest_mesas[dir] = mesa2
                    else:
                        closest_mesas[dir] = mesa2
            for dir in ['N', 'E', 'S', 'W']:
                if closest_mesas[dir] != None and random.randint(0, 3) == 0:
                    self.make_bridge(mesa, closest_mesas[dir], dir)

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
            y = self.height//2
            x = r*(self.width//5) + 5
            # y = r*(self.height//5) + 5
            # x = self.width//2
            self.make_mesa(x-r, y-r, r)
            self.set(x, y, TileManager.test_tile)
        self.make_bridge(self._mesas[2], self._mesas[3], 'E')

    def get_map_array(self):
        return self._maparray

    def make_mesa(self, x, y, r):
        """Generates a new mesa with radius r and adds it to the map with its top-left corner at x,y"""
        new_mesa = Mesa(x, y, r)
        self._mesas.append(new_mesa)
        self.apply_patch(new_mesa)

    def make_bridge(self, mesa, mesa2, dir):
        y = None
        x = None
        length = None
        if dir in ['E', 'W']:
            max_y = min(mesa.y + mesa.height, mesa2.y + mesa2.height)
            min_y = max(mesa.y, mesa2.y)
            y = random.randint(min_y, max_y-1)
        elif dir in ['N', 'S']:
            max_x = min(mesa.x + mesa.width, mesa2.x + mesa2.width)
            min_x = max(mesa.x, mesa2.x)
            x = random.randint(min_x, max_x-1)
        if x == None:
            #Bridge is horizontal
            x = self._get_bridge_coordinate(y, mesa.center_y, mesa.center_x, mesa.get_ribwidth, invert=(dir=='W'))
            other_x = self._get_bridge_coordinate(y, mesa2.center_y, mesa2.center_x, mesa2.get_ribwidth, invert=(dir=='E'))
            length = abs(x - other_x) + 1
        if y == None:
            #Bridge is vertical
            y = self._get_bridge_coordinate(x, mesa.center_x, mesa.center_y, mesa.get_ribwidth, invert=(dir=='N'))
            other_y = self._get_bridge_coordinate(x, mesa2.center_x, mesa2.center_y, mesa2.get_ribwidth, invert=(dir=='S'))
            length = abs(y - other_y) + 1

        directions = {'N': (0,-1),
                    'E': (1,0),
                    'S': (0,1),
                    'W': (-1,0)}
        new_bridge = Bridge(x, y, length, directions[dir])
        self._bridges.append(new_bridge)
        self.apply_patch(new_bridge)

    def _get_bridge_coordinate(self, b, center_b, center_c, ribwidth_func, invert=False):
        """b is an x or y coordinate
            center_b is the center x or y coordinate of the mesa
            center_b is the coordinate along the perpendicular axis
            ribwidth_func is the mesa's get_ribwidth
            invert = true if the bridge is pointing in the negative direction
            Returns a global coordinate of a point on the edge of a mesa
            along an axis perpendicular to b.
            """
        circ_bridge_coord = b - center_b
        c_offset = ribwidth_func(circ_bridge_coord) + 1
        if invert:
            c_offset *= -1
        return center_c + c_offset


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