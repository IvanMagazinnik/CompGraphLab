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


def tex_coord(x, y, n=4):
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


TEXTURE_PATH = 'texture.png'
#TEXTURE_PATH = 'big_texture.png'
#TEXTURE_PATH = 'image.png'

GRASS = tex_coords((1, 0), (0, 1), (0, 0))
#GRASS = tex_coords((4, 15), (3, 15), (3, 15))
SAND = tex_coords((1, 1), (1, 1), (1, 1))
BRICK = tex_coords((2, 0), (2, 0), (2, 0))
STONE = tex_coords((2, 1), (2, 1), (2, 1))

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
menu_img = image.load(IMG_MENU)
selected_img = image.load(IMG_SELECTED)
