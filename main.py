import random
import math

class Map(object):
    floor = '.'
    wall = '#'
    impass = '~'

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self._maparray = []

        for y in range(self.height):
            self._maparray.append([])
            for x in range(self.width):
                self._maparray[y].append(Map.impass)

        self._create_map()

    def get(self, x, y):
        return self._maparray[y][x]

    def set(self, x, y, tile):
        self._maparray[y][x] = tile

    def _create_map(self):
        num_dolmens = 5
        dolmen_radius = 6
        for i in range(num_dolmens):
            x = random.randint(0, self.width-1)
            y = random.randint(0, self.height-1)
            r = random.randint(0, dolmen_radius)
            self.make_dolmen(x, y, r)
        # test_dolmens()

        for i_y, row in enumerate(self._maparray):
            for i_x, tile in enumerate(row):
                if tile == Map.floor:
                    for neighbor in get_orthog_neighbors(i_x, i_y):
                        if neighbor[0] < self.width and neighbor[1] < self.height and self.get(neighbor[0], neighbor[1]) == Map.impass:
                            self.set(neighbor[0], neighbor[1], Map.wall)

    def show_map(self):
        for row in self._maparray:
            rowstring = ""
            for tile in row:
                rowstring += tile
            print rowstring

    def make_dolmen(self, x, y, r):
        for circ_height in range(-r, r+1):
            circ_width = int(get_circle_dimensions(r, circ_height))
            for circ_x in range(x-circ_width, x+circ_width+1):
                if y+circ_height < self.height and circ_x < self.width:
                    self.set(circ_x, y+circ_height, Map.floor)


def get_circle_dimensions(r, y):
    return math.sqrt(r**2 - y**2)


def test_dolmens():
    for r in range(0, 5):
        x = width/2
        y = r*(height/5) + 5
        make_dolmen(x, y, r)
        map.set(x, y, '@')

def get_orthog_neighbors(x, y):
   return [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]

if __name__ == "__main__":
    map = Map(50, 50)
    map.show_map()

