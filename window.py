# -*- coding: utf-8 -*-
from world import *
from cube import *

from pyglet.gl import *
from pyglet.window import key, mouse
from cube import selected_img, menu_img

class Window(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)

        # Параметр захвата мыши
        self.is_mouse_grab = False

        # Полет персонажа
        self.is_fly = False

        # направление движения первая колонка +1 назад -1 вперед вторая аналогично для лево право 0 нет движения
        self.move_direction = [0, 0]

        self.position = (0, 0, 0)

        # поворотноый вектор. 1 элемент поворот в плоскости земли - неограничен (x-z)
        # 2 элемент поворот по оси OY вверх вниз ограничен [-90,90]
        self.rotation = (0, 0)

        # на каком кубике в плоскости x-z нах-ся персоонаж
        self.cube_pos = None

        # Прицел
        self.aim = None

        # menu
        self.menu_selector = pyglet.graphics.Batch()

        # Скорость движения по y тк она не константа а модифицируется гравитацие выносится отдельно
        self.dy = 0

        # Список доступных игроку кубов
        self.player_cube = [BRICK, GRASS, SAND]

        # Текущий куб игрока
        self.block = self.player_cube[0]
        self.selected_block = 0

        self.label = pyglet.text.Label('', font_name='Arial', font_size=18,
                                        x=10, y=self.height - 10, anchor_x='left', anchor_y='top',
                                        color=(0, 0, 0, 255))

        # Это введено для ужобства из-за отсутствия switch case конструкции и для будующих расширений
        self.num_keys = [
            key._1, key._2, key._3, key._4, key._5,
            key._6, key._7, key._8, key._9, key._0]

        # объект класса мир
        self.world = World()

        pyglet.clock.schedule_interval(self.update, 1.0 / TICKS_PER_SEC)

    def set_exclusive_mouse(self, exclusive):
        # захват мыши экраном
        super(Window, self).set_exclusive_mouse(exclusive)
        self.is_mouse_grab = exclusive

    def get_sight_vector(self):
        # Определение нормированного вектора направления камеры вычисляется переходом от сферических rotation
        # координат к декартовым

        phi, psi = self.rotation

        m = math.cos(math.radians(psi))

        dy = math.sin(math.radians(psi))
        dx = math.sin(math.radians(phi)) * m
        dz = -1 * math.cos(math.radians(phi)) * m
        return dx, dy, dz

    def get_motion_vector(self):
        # Вычисление вектора движения игрока отражающую скорость игрока

        # если задано направление движения
        if any(self.move_direction):
            x, y = self.rotation
            # направление задаваемое стрелочками по факту имеет 8 значенией с шагом 45 от -180 до 180
            move_direction = math.degrees(math.atan2(self.move_direction[0], self.move_direction[1]))
            y_angle = math.radians(y)
            x_angle = math.radians(x + move_direction)
            if self.is_fly:
                dy = math.sin(y_angle)
                if self.move_direction[1]:
                    # Двидение лево право
                    dy = 0.0
                if self.move_direction[0] > 0:
                    # Движение назад
                    dy *= -1
                dx = math.cos(x_angle)
                dz = math.sin(x_angle)
            else:
                dy = 0.0
                dx = math.cos(x_angle)
                dz = math.sin(x_angle)
        else:
            dy = 0.0
            dx = 0.0
            dz = 0.0
        return dx, dy, dz

    def update(self, dt):
        # функция обновления экрана вызываемая часа pyglet с параметром dt - время прошедшее с последнего вызова функции
        self.world.process_queue()
        sector = get_sector(self.position)
        if sector != self.cube_pos:
            self.world.change_sectors(self.cube_pos, sector)
            if self.cube_pos is None:
                self.world.process_entire_queue()
            self.cube_pos = sector
        m = 8
        dt = min(dt, 0.2)
        for _ in xrange(m):
            self.player_move(dt / m)

    def player_move(self, dt):
        # Фуекци обработки перемещения игрока с колизией прыжками и т.п

        # перемещение
        speed = FLYING_SPEED if self.is_fly else WALKING_SPEED
        d = dt * speed # distance covered this tick.
        dx, dy, dz = self.get_motion_vector()
        # новая позиция без учета гравитации
        dx, dy, dz = dx * d, dy * d, dz * d
        # применение гравитации при полете
        if not self.is_fly:
            # Изменение вертикаотной скорости от гравитации
            self.dy -= dt * GRAVITY
            self.dy = max(self.dy, -MAX_VELOCITY)
            dy += self.dy * dt
        # вычисление коллизий
        x, y, z = self.position
        x, y, z = self.collide((x + dx, y + dy, z + dz), PLAYER_HEIGHT)
        self.position = (x, y, z)

    def collide(self, position, height):
        # Проверка коллизий
        fat = 0.25
        p = list(position)
        np = normal(position)
        for face in FACES:
            for i in xrange(3):
                if not face[i]:
                    continue
                d = (p[i] - np[i]) * face[i]
                if d < fat:
                    continue
                for dy in xrange(height):
                    op = list(np)
                    op[1] -= dy
                    op[i] += face[i]
                    if tuple(op) not in self.world.world:
                        continue
                    p[i] -= (d - fat) * face[i]
                    # Коллизии при падении
                    if face == (0, -1, 0) or face == (0, 1, 0):
                        self.dy = 0
                    break
        return tuple(p)

    def on_mouse_press(self, x, y, button, modifiers):
        # Если мышь захвачена то работаем с кубами, создаем или удаляем
        if self.is_mouse_grab:
            vector = self.get_sight_vector()
            block, previous = self.world.hit_test(self.position, vector)
            if button == mouse.RIGHT:
                if previous:
                    self.world.add_block(previous, self.block)
            elif button == pyglet.window.mouse.LEFT and block:
                texture = self.world.world[block]
                if texture != STONE:
                    self.world.remove_block(block)
        # Иначе захватываем мышь
        else:
            self.set_exclusive_mouse(True)

    def on_mouse_motion(self, x, y, dx, dy):
        # Обработка движения мыши - вращение камеры
        if self.is_mouse_grab:
            sensitivity = 0.15
            x, y = self.rotation
            x, y = x + dx * sensitivity, y + dy * sensitivity
            y = max(-90, min(90, y))
            self.rotation = (x, y)

    def on_key_press(self, symbol, modifiers):
        # Обработка нажатий на кнопку
        if symbol == key.W:
            self.move_direction[0] -= 1
        elif symbol == key.S:
            self.move_direction[0] += 1
        elif symbol == key.A:
            self.move_direction[1] -= 1
        elif symbol == key.D:
            self.move_direction[1] += 1
        elif symbol == key.SPACE:
            if self.dy == 0:
                self.dy = JUMP_SPEED
        elif symbol == key.ESCAPE:
            self.set_exclusive_mouse(False)
        elif symbol == key.TAB:
            self.is_fly = not self.is_fly
        elif symbol in self.num_keys:
            index = (symbol - self.num_keys[0]) % 9
            self.block = self.player_cube[index % len(self.player_cube)]
            self.selected_block = index

    def on_key_release(self, symbol, modifiers):
        if symbol == key.W:
            self.move_direction[0] += 1
        elif symbol == key.S:
            self.move_direction[0] -= 1
        elif symbol == key.A:
            self.move_direction[1] += 1
        elif symbol == key.D:
            self.move_direction[1] -= 1

    def on_resize(self, width, height):
        # автовызываемая функция pyglet ищменения при ресайзе окна
        # aim
        if self.aim:
            self.aim.delete()
        x, y = self.width / 2, self.height / 2
        n = 10
        self.aim = pyglet.graphics.vertex_list(4,
            ('v2i', (x - n, y, x + n, y, x, y - n, x, y + n))
        )

    def set_2d(self):
        # Конфигурация opengl  в 2d для отрисовки прицела
        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def vec(args):
        return (GLfloat * len(args))(args)

    def set_3d(self):
        # Конфигурация opengl для отрисовки 3d  здесь же вся работа с камерой, тюе поварот на
        # два угла это повороты камеры а также перемещение всех объектов от себя на свои координаты
        # + настройка переспективных преобразований
        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(65.0, width / float(height), 0.1, 60.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        x, y = self.rotation
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = self.position
        glTranslatef(-x, -y, -z)
        setup_light()

    def on_draw(self):
        # авто функция pyglet отрисовки экрана
        self.clear()
        self.set_3d()
        glColor3d(1, 1, 1)
        self.world.batch.draw()
        self.draw_focused_block()
        self.set_2d()
        self.draw_aim()
        self.draw_fps()
        self.draw_cube_selector()

    def draw_focused_block(self):
        # Выделение блока на с которым пересекается вектор взгляда персонажа
        vector = self.get_sight_vector()
        block = self.world.hit_test(self.position, vector)[0]
        if block:
            x, y, z = block
            vertex_data = cube_vertices(x, y, z, 0.51)
            glColor3d(0, 0, 0)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            pyglet.graphics.draw(24, GL_QUADS, ('v3f/static', vertex_data))
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def draw_fps(self):
        self.label.text = 'fps = %02d' % (
            pyglet.clock.get_fps())
        self.label.draw()

    def draw_aim(self):
        # отрисовка прицела
        self.aim.draw(GL_LINES)

    def draw_cube_selector(self):
        sprites = []
        start_pos = self.width/2 - 40*4.5
        selected_menu = pyglet.sprite.Sprite(selected_img, x=start_pos + self.selected_block * 40 - 4, y=27,
                                             batch=self.menu_selector)
        menu = pyglet.sprite.Sprite(menu_img, x=start_pos, y=30, batch=self.menu_selector)


        self.menu_selector.draw()


def setup_fog():
    # Настройка тумана для адекватной дальности обзора
    glEnable(GL_FOG)
    glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0.5, 0.69, 1.0, 1))
    glHint(GL_FOG_HINT, GL_DONT_CARE)
    glFogi(GL_FOG_MODE, GL_LINEAR)
    glFogf(GL_FOG_START, 20.0)
    glFogf(GL_FOG_END, 60.0)


def setup_light():
    # Настройка освещения
    glEnable(GL_LIGHTING)
    glLightModelf(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)
    glEnable(GL_NORMALIZE)
    glMaterialfv(GL_FRONT, GL_AMBIENT,(GLfloat * 4)(1.0,1.0,1.0,1.0))
    glMaterialfv(GL_BACK, GL_AMBIENT,(GLfloat * 4)(0.2,0.2,0.2,0.2))
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (GLfloat * 4)(0.0,0.0,1.0,0.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (GLfloat * 4)(1.0,1.0,1.0,0.0))


def setup():
    # Стартовый конфиг opengl
    glClearColor(0.5, 0.69, 1.0, 1)
    glEnable(GL_CULL_FACE)
    # glEnable(GL_LIGHTING)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    setup_fog()


def main():
    window = Window(width=800, height=600, caption='Pyglet', resizable=True)
    window.set_exclusive_mouse(True)
    setup()
    pyglet.app.run()


if __name__ == '__main__':
    main()
