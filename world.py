# -*- coding: utf-8 -*-
from collections import deque
from pyglet import image
from pyglet.graphics import TextureGroup
from pyglet.gl import *
import random
import time
from cube import *


# Идея такова что мы разгружаем отрисовку всего мира на посекторную отрисовку в зависимости от позиции соответственно
# пересчет всех углов и т.п идет только в секторе

class World(object):

    def __init__(self):

        # pyglet тип - заданный набор вершин, по факту определяет любую фигуру
        self.batch = pyglet.graphics.Batch()

        # Текстурный объект
        self.texture = TextureGroup(TEXTURE.get_texture())

        # описание всех блоков в мире
        self.world = {}

        # описание всех видимых блоков в мире
        self.shown = {}

        # Mapping позиций кубов в pyglet VertexList
        self._shown = {}

        self.sectors = {}

        self.queue = deque()

        self._initialize()

    def _initialize(self):
        # Инициализация мира кубами
        n = 80
        s = 1
        y = 0
        for x in xrange(-n, n + 1, s):
            for z in xrange(-n, n + 1, s):
                # Земля
                self.add_block((x, y - 2, z), GRASS, immediate=False)
                self.add_block((x, y - 3, z), STONE, immediate=False)
                if x in (-n, n) or z in (-n, n):
                    # Стена по краю
                    for dy in xrange(-2, 3):
                        self.add_block((x, y + dy, z), STONE, immediate=False)
        self.generate_random_hill()

    def generate_random_hill(self):
        n = WORLD_SIZE
        o = n - 10
        for _ in xrange(120):
            a = random.randint(-o, o)
            b = random.randint(-o, o)
            c = -1
            h = random.randint(1, 6)
            s = random.randint(4, 8)
            d = 1
            t = random.choice([GRASS, SAND, BRICK,WOOD,TREE])
            for y in xrange(c, c + h):
                for x in xrange(a - s, a + s + 1):
                    for z in xrange(b - s, b + s + 1):
                        if (x - a) ** 2 + (z - b) ** 2 > (s + 1) ** 2:
                            continue
                        if (x - 0) ** 2 + (z - 0) ** 2 < 5 ** 2:
                            continue
                        self.add_block((x, y, z), t, immediate=False)
                s -= d
        pass

    def hit_test(self, position, vector, max_distance=MAX_DRAW_LENGTH):
        # Проверка пересечения вектора взгляда и куба возвращает куб пересечения и предыдущий куб
        m = 8
        x, y, z = position
        dx, dy, dz = vector
        previous = None
        for _ in xrange(max_distance * m):
            key = normal((x, y, z))
            if key != previous and key in self.world:
                return key, previous
            previous = key
            x, y, z = x + dx / m, y + dy / m, z + dz / m
        return None, None

    def exposed(self, position):
        # Проверка можно ли поставить к кубу еще кубик
        x, y, z = position
        for dx, dy, dz in FACES:
            if (x + dx, y + dy, z + dz) not in self.world:
                return True
        return False

    def add_block(self, position, texture, immediate=True):
        # Добавление кубика в позиции куда смотрит вектор взгляда
        if position in self.world:
            self.remove_block(position, immediate)
        self.world[position] = texture
        self.sectors.setdefault(get_sector(position), []).append(position)
        if immediate:
            if self.exposed(position):
                self.show_block(position)
            self.check_neighbors(position)

    def remove_block(self, position, immediate=True):
        # Удаление блока
        del self.world[position]
        self.sectors[get_sector(position)].remove(position)
        if immediate:
            if position in self.shown:
                self.hide_block(position)
            self.check_neighbors(position)

    def check_neighbors(self, position):
        x, y, z = position
        for dx, dy, dz in FACES:
            key = (x + dx, y + dy, z + dz)
            if key not in self.world:
                continue
            if self.exposed(key):
                if key not in self.shown:
                    self.show_block(key)
            else:
                if key in self.shown:
                    self.hide_block(key)

    def __show_block(self,position, imediate = True):
        texture = self.world[position]


    def show_block(self, position, immediate=True):
        # Отображение скрытого блока в позиции
        texture = self.world[position]
        self.shown[position] = texture
        if immediate:
            self._show_block(position, texture)
        else:
            self._enqueue(self._show_block, position, texture)

    def _show_block(self, position, texture):
        # Mapping позиции куба в pyglet VertexList
        x, y, z = position
        vertex_data = cube_vertices(x, y, z, 0.5)
        texture_data = list(texture)

        self._shown[position] = self.batch.add(24, GL_QUADS, self.texture,
            ('v3f/static', vertex_data),
            ('t2f/static', texture_data))

    def hide_block(self, position, immediate=True):
        # Скрыть куб
        self.shown.pop(position)
        if immediate:
            self._hide_block(position)
        else:
            self._enqueue(self._hide_block, position)

    def _hide_block(self, position):
        self._shown.pop(position).delete()

    def show_sector(self, sector):
        for position in self.sectors.get(sector, []):
            if position not in self.shown and self.exposed(position):
                self.show_block(position, False)

    def hide_sector(self, sector):
        for position in self.sectors.get(sector, []):
            if position in self.shown:
                self.hide_block(position, False)

    def change_sectors(self, before, after):
        before_set = set()
        after_set = set()
        pad = 4
        for dx in xrange(-pad, pad + 1):
            for dy in [0]:
                for dz in xrange(-pad, pad + 1):
                    if dx ** 2 + dy ** 2 + dz ** 2 > (pad + 1) ** 2:
                        continue
                    if before:
                        x, y, z = before
                        before_set.add((x + dx, y + dy, z + dz))
                    if after:
                        x, y, z = after
                        after_set.add((x + dx, y + dy, z + dz))
        show = after_set - before_set
        hide = before_set - after_set
        for sector in show:
            self.show_sector(sector)
        for sector in hide:
            self.hide_sector(sector)

    def _enqueue(self, func, *args):
        self.queue.append((func, args))

    def _dequeue(self):
        func, args = self.queue.popleft()
        func(*args)

    def process_queue(self):
        start = time.clock()
        while self.queue and time.clock() - start < 1.0 / TICKS_PER_SEC:
            self._dequeue()

    def process_entire_queue(self):
        while self.queue:
            self._dequeue()
