from __future__ import division

import math

from tilemanager import TileManager

class Patch(object):
    """A grid of tiles that can be added onto the map."""

    def __init__(self, x, y, height, width):
        #x,y are the origin-tile in the upper-left corner.
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self._patch = [[None for i in range(self.width)]for j in range(self.height)]

    def get(self, x, y):
        return self._patch[y][x]

    def set(self, x, y, tile):
        self._patch[y][x] = tile

    def dbgoutput(self):
        dbgstr = "X:{0} Y:{1} width:{2} height:{3}".format(self.x, self.y, self.width, self.height)
        return dbgstr + '\n' + self.__str__()

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


class Mesa(Patch):
    """A circular island"""

    def __init__(self, x, y, r):
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

    def get_ribwidth(self, offset):
        """Returns the perpendicular distance to the edge of the circle from a line
        through the center of the circle at a given offset.
        """
        return int(math.sqrt(abs(self.r**2 - offset**2)))

    def get_edge_coordinates(self, offset_from_center, axis, invert=False):
        """ Returns the coordinates of a point on the edge of the mesa perpendicular
            to a given axis at a given offset from the center.
            offset_from_center is the number of tiles away from the center along the specified axis
            axis is 0 if x, 1 if y
            invert = true if the edge should be in the negative direction.
            """
        circle_space_perp_coord = self.get_ribwidth(offset_from_center) + 1
        if invert:
            circle_space_perp_coord *= -1
        perp_coord = circle_space_perp_coord + (self.center_y, self.center_x)[axis]
        par_coord = offset_from_center + (self.center_x, self.center_y)[axis]
        return ((par_coord, perp_coord), (perp_coord, par_coord))[axis]


class Bridge(Patch):
    """A straight row of walkable tiles; a rickety wooden bridge over the sea"""

    def __init__(self, x, y, length, direction):
        self.x = x
        self.y = y

        self.length = length

        self._patch = [[]]
        self.width = 0
        self.height = 0
        self._build_bridge(direction)

    def _build_bridge(self, direction):
        self.width = max(abs(self.length * direction[0]), 1)
        self.height = max(abs(self.length * direction[1]), 1)
        self.x = min(self.x, self.x + (self.length * direction[0]) + 1)
        self.y = min(self.y, self.y + (self.length * direction[1]) + 1)
        self._patch = [[TileManager.bridge for i in range(self.width)]for j in range(self.height)]
