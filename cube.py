# -*- coding: utf-8 -*-
from constant_def import *
from pyglet import image

def cube_vertices(x, y, z, n):
    # Массив вершин куба в позиции x y z ширины 2n
    return [
        x-n,y+n,z-n, x-n,y+n,z+n, x+n,y+n,z+n, x+n,y+n,z-n,  # top
        x-n,y-n,z-n, x+n,y-n,z-n, x+n,y-n,z+n, x-n,y-n,z+n,  # bottom
        x-n,y-n,z-n, x-n,y-n,z+n, x-n,y+n,z+n, x-n,y+n,z-n,  # left
        x+n,y-n,z+n, x+n,y-n,z-n, x+n,y+n,z-n, x+n,y+n,z+n,  # right
        x-n,y-n,z+n, x+n,y-n,z+n, x+n,y+n,z+n, x-n,y+n,z+n,  # front
        x+n,y-n,z-n, x-n,y-n,z-n, x-n,y+n,z-n, x+n,y+n,z-n,  # back
    ]


def tex_coord(x, y, n=16):
    # координты конкретной части текстуры из файлика
    m = 1.0 / n
    dx = x * m
    dy = y * m
    return dx, dy, dx + m, dy, dx + m, dy + m, dx, dy + m


def tex_coords(top, bottom, side):
    # Координаты всех текстур для кубика туплом
    top = tex_coord(*top)
    bottom = tex_coord(*bottom)
    side = tex_coord(*side)
    result = []
    result.extend(top)
    result.extend(bottom)
    result.extend(side * 4)
    return result


TEXTURE_PATH = 'textures/texture_pack.png'

TEXTURE = image.load(TEXTURE_PATH)

GRASS = tex_coords((1, 15), (2, 15), (2, 15))
SAND = tex_coords((4, 13), (4, 13), (4, 13))
BRICK = tex_coords((5, 10), (5, 10), (5, 10))
STONE = tex_coords((15, 6), (15, 6), (15, 6))
WOOD = tex_coords((5, 15), (5, 15), (5, 15))
TREE = tex_coords((3, 14), (3, 14), (4, 14))

FACES = [
    ( 0, 1, 0),
    ( 0,-1, 0),
    (-1, 0, 0),
    ( 1, 0, 0),
    ( 0, 0, 1),
    ( 0, 0,-1),
]


def normal(position):
    # Округление координат
    x, y, z = position
    x, y, z = (int(round(x)), int(round(y)), int(round(z)))
    return (x, y, z)


def get_sector(position):
    # вычисление сектора в котором мы находимся для упрощенной отрисовки кубика на котором мы находимся
    x, y, z = normal(position)
    x, y, z = x / SECTOR_SIZE, y / SECTOR_SIZE, z / SECTOR_SIZE
    return (x, 0, z)


# Menu section

IMG_SELECTED = 'textures/selected_menu.png'
IMG_MENU = 'textures/menu.png'
IMG_GRASS = 'textures/grass_img.png'
IMG_BRICK = 'textures/brick_img.png'
IMG_SAND = 'textures/sand_img.png'
IMG_WOOD = 'textures/wood_img.png'
IMG_WOOD_PART = 'textures/wood_part_img.png'

menu_img = image.load(IMG_MENU)
selected_img = image.load(IMG_SELECTED)
img_grass = image.load(IMG_GRASS)
img_brick = image.load(IMG_BRICK)
img_sand = image.load(IMG_SAND)
img_wood = image.load(IMG_WOOD)
img_wood_part = image.load(IMG_WOOD_PART)