import random
import math

width = 50
height = 50

floor = '.'
wall = '*'
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


    

for row in map:
    rowstring = ""
    for tile in row:
        rowstring += tile
    print rowstring
