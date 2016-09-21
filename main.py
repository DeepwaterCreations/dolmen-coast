import random
import math

width = 50
height = 50

floor = '.'
wall = '#'
impass = '~'

map = []
for y in range(height):
    map.append([])
    for x in range(width):
        map[y].append(impass)

def get_circle_dimensions(r, y):
    return math.sqrt(r**2 - y**2)

def make_dolmen(x, y, r):
    for circ_height in range(-r, r+1):
        circ_width = int(get_circle_dimensions(r, circ_height))
        for circ_x in range(x-circ_width, x+circ_width+1):
            if y+circ_height < height and circ_x < width:
                map[y+circ_height][circ_x] = floor

def test_dolmens():
    for r in range(0, 5):
        x = width/2
        y = r*(height/5) + 5
        make_dolmen(x, y, r)
        map[y][x] = '@'

num_dolmens = 5
dolmen_radius = 6
for i in range(num_dolmens):
    x = random.randint(0, width-1)
    y = random.randint(0, height-1)
    r = random.randint(0, dolmen_radius)
    print x, y, r
    make_dolmen(x, y, r)
# test_dolmens()

def get_orthog_neighbors(x, y):
   return [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]

for i_y, row in enumerate(map):
    for i_x, tile in enumerate(row):
        if tile == floor:
            for neighbor in get_orthog_neighbors(i_x, i_y):
                if neighbor[0] < width and neighbor[1] < height and map[neighbor[1]][neighbor[0]] == impass:
                    map[neighbor[1]][neighbor[0]] = wall

for row in map:
    rowstring = ""
    for tile in row:
        rowstring += tile
    print rowstring
