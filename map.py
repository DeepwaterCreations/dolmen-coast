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
        try:
            self._maparray[y][x] = tile
        except IndexError as e:
            raise IndexError(e.args[0] + " X:{0} Y:{1} Width:{2} Height:{3}".format(x, y, self.width, self.height))

    def _create_map(self):
        # self._create_map_default()
        self._create_map_bsp(0, 0, self.width-1, self.height-1)

    def _create_map_default(self):
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

        self._build_mesa_walls()
    
    def _create_map_bsp(self, x, y, width, height, iter=0):
        # http://roguecentral.org/doryen/articles/bsp-dungeon-generation/
        margin = 4
        max_iters = 10
        if width <= 2*margin and height <= 2*margin or iter >= max_iters:
            #End case
            #Build mesa
            mesa_x = random.randint(x, (x + width)-1)
            mesa_y = random.randint(y, (y + height)-1)
            maxradius = (min((x+width) - mesa_x, (y+height) - mesa_y)-1)//2
            mesa_r = 0 if maxradius <= 0 else random.randint(0, maxradius)

            new_mesa = Mesa(mesa_x, mesa_y, mesa_r)
            if new_mesa.x + new_mesa.width >= self.width or new_mesa.y + new_mesa.height >= self.height:
                raise IndexError("Mesa X:{0} Mesa Y{1} Mesa R:{2} \n{3}".format( mesa_x, mesa_y, mesa_r, new_mesa.dbgoutput()))
            self._mesas.append(new_mesa)
            self.apply_patch(new_mesa)
            return [new_mesa]
        else:
            #Recursive step
            split_dir, split_pos = self._get_bsp_partition(x, y, width, height, margin)
        #TODO: Terminate or not based on size? That should actually be decided before we do the partition.
        # if iter < max_iters:
        # if width * height > 100 
            new_width_1 = width if split_dir == 'h' else split_pos - x
            new_width_2 = width if split_dir == 'h' else (x + width) - split_pos
            new_height_1 = height if split_dir == 'v' else split_pos - y
            new_height_2 = height if split_dir == 'v' else (y + height) - split_pos
            x1 = x
            x2 = x if split_dir == 'h' else split_pos
            y1 = y
            y2 = y if split_dir == 'v' else split_pos

            mesas_a = self._create_map_bsp(x1, y1, new_width_1, new_height_1, iter + 1)
            mesas_b = self._create_map_bsp(x2, y2, new_width_2, new_height_2, iter + 1)

            #Join the two partitions via a bridge
            #I need to find a pair of mesas, one in each partition, that are orthogonally colinear
            #and that don't have mesas between them.
            #For the first condition, I have that solved.
            #For the second, I can check the other mesas' bounding boxes
            #against a box around mesa a and mesa b.
            #BSP is great for making sure my graph is fully connected, but
            #not so great for precomputing any of this stuff, alas.
        #TODO: Get back the next iteration's partitions/mesas, join them together with a bridge.

    def _get_bsp_partition(self, x, y, width, height, margin):
        if width <= 2*margin:
            split_dir = 'h'
        elif height <= 2*margin:
            split_dir = 'v'
        else:
            #Weight direction based on ratio so I can try for more square-shaped sections
            #First, set a threshold between 1 and -1. Selecting above the threshold will
            #make a vertical slice, and selecting below it will make a horizontal one.
            #The threshold is based on the ratio between the width and the height. Tall, skinny
            #boxes get a >0 ratio. Short, fat ones get <0.
            aspect_ratio = 1 - (width/height) if height > width else -(1 - height/width)
            #Select a random number between -1 and 1, weighted toward 0 via a beta distribution.
            #This will weight the selection in favor of partitions that make the resulting boxes more "square"
            #since a random number at 0 will select whatever the threshold decided was the short axis.
            dir_select_num = (random.betavariate(5, 5) * 2) - 1
            split_dir = 'v' if dir_select_num > aspect_ratio else 'h'
        #Now that we have an axis, pick a random position for the split between the ends of the box,
        #offset by the specified margin.
        min_bound = (y + margin) if split_dir == 'h' else (x + margin)
        max_bound = ((y + height) - margin) if split_dir == 'h' else ((x + width) - margin)
        #TODO: Should this also be a beta distribution? Sure, why not, yeah?
        split_pos = random.randint(min_bound, max_bound)

        #TEST: Draw test tiles along the partition edge to visualize it.
        for tile_x in range(x, x+width):
            for tile_y in range(y, y+height):
                if (split_dir == 'h' and tile_y == split_pos) or (split_dir == 'v' and tile_x == split_pos):
                        self.set(tile_x, tile_y, TileManager.test_tile)
        #End test code

        return split_dir, split_pos

    def _build_mesa_walls(self):
        """For each floor tile on the map, turn all orthogonal neighbors that are impass
        tiles into wall tiles.
        """
        for i_y, row in enumerate(self._maparray):
            for i_x, tile in enumerate(row):
                if tile == TileManager.floor:
                    for neighbor in get_orthog_neighbors(i_x, i_y):
                        if neighbor[0] < self.width and neighbor[1] < self.height and self.get(neighbor[0], neighbor[1]) == TileManager.impass:
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


    def apply_patch(self, patchsource):
        """Adds a set of tiles to the map from an object that has a patch and a set of x,y coordinates"""
        patch = patchsource._patch
        for i_y, row in enumerate(patch):
            for i_x, tile in enumerate(row):
                if i_y+patchsource.y >= self.height or i_x+patchsource.x >= self.width:
                    raise IndexError("Patch out of bounds w{0} h{1} at {2},{3}:\n \
                            {4}".format(self.width, self.height, i_x+patchsource.x, i_y+patchsource.y, patchsource.dbgoutput()))
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
