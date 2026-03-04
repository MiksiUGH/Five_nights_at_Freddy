"""Модуль персонажей игры Five Nights at Freddy's.

Содержит классы игрока (ночного сторожа) и аниматроников: Бонни, Чика, Фокси, Фредди.
"""


import math
import random
import arcade


class NightGuard(arcade.Sprite):
    """Класс игрока — ночного сторожа.

    Управляется с клавиатуры, имеет анимации движения в разных направлениях.
    """

    def __init__(self):
        """Создаёт спрайт сторожа, загружает текстуры и настраивает анимацию."""
        super().__init__(scale=1.3)

        self.idle_texture = arcade.load_texture("images/player/sprite4.png")
        self.walk_right_textures = [
            arcade.load_texture("images/player/sprite0.png"),
            arcade.load_texture("images/player/sprite1.jpg"),
            arcade.load_texture("images/player/sprite2.png"),
            arcade.load_texture("images/player/sprite3.jpg"),
        ]
        self.walk_left_textures = [
            tex.flip_horizontally() for tex in self.walk_right_textures
        ]
        self.walk_up_textures = [
            arcade.load_texture("images/player/sprite8.png"),
            arcade.load_texture("images/player/sprite9.png"),
            arcade.load_texture("images/player/sprite10.png"),
            arcade.load_texture("images/player/sprite11.png"),
        ]
        self.walk_down_textures = [
            arcade.load_texture("images/player/sprite4.png"),
            arcade.load_texture("images/player/sprite5.png"),
            arcade.load_texture("images/player/sprite6.png"),
            arcade.load_texture("images/player/sprite7.png"),
        ]

        self.texture = self.idle_texture
        self.speed = 5

        self.cur_texture_index = 0
        self.animation_time = 0.15
        self.time_since_last_frame = 0
        self.facing_direction = 1  # 1 - вправо, -1 - влево

    def update_animation(self, dt: float = 1 / 60):
        """Обновляет кадр анимации в зависимости от направления движения.

        :param dt: время с предыдущего кадра
        :type dt: float
        """
        self.time_since_last_frame += dt

        if self.change_x != 0:
            if self.change_x > 0:
                textures = self.walk_right_textures
                self.facing_direction = 1
            else:
                textures = self.walk_left_textures
                self.facing_direction = -1

            if self.time_since_last_frame >= self.animation_time:
                self.cur_texture_index = (self.cur_texture_index + 1) % len(textures)
                self.texture = textures[self.cur_texture_index]
                self.time_since_last_frame = 0

        elif self.change_y != 0:
            if self.change_y > 0:
                textures = self.walk_up_textures
            else:
                textures = self.walk_down_textures

            if self.time_since_last_frame >= self.animation_time:
                self.cur_texture_index = (self.cur_texture_index + 1) % len(textures)
                self.texture = textures[self.cur_texture_index]
                self.time_since_last_frame = 0

        else:
            self.texture = self.idle_texture
            self.cur_texture_index = 0
            self.time_since_last_frame = 0


class Freddy(arcade.Sprite):
    """Аниматроник Фредди.

    После активации исчезает и начинает следить за неподвижностью игрока.
    """

    def __init__(self):
        """Загружает текстуры и звуки, инициализирует состояние."""
        super().__init__(scale=1.3)

        self.jumpscare = arcade.load_texture('images/freddy/jumpscare.jpg')
        self.jumpscare_sound = arcade.load_sound('sounds/scearm_sound.mp3')
        self.not_activate = arcade.load_texture('images/freddy/sprite00.png')

        self.state = "inactive"
        self.texture = self.not_activate
        self.alpha = 255


class Bonnie(arcade.Sprite):
    """Аниматроник Бонни.

    Патрулирует случайным образом, переходит в погоню, если видит игрока.
    """

    def __init__(self):
        """Загружает текстуры, звуки, задаёт начальные параметры."""
        super().__init__(scale=1.3)

        self.activated = False
        self.jumpscare = arcade.load_texture('images/bonnie/jumpscare.jpg')
        self.jumpscare_sound = arcade.load_sound('sounds/scearm_sound.mp3')
        self.not_activate = arcade.load_texture('images/bonnie/sprite00.png')
        self.idle_texture = arcade.load_texture("images/bonnie/sprite4.png")
        self.walk_right_textures = [
            arcade.load_texture("images/bonnie/sprite0.png"),
            arcade.load_texture("images/bonnie/sprite1.png"),
            arcade.load_texture("images/bonnie/sprite2.png"),
            arcade.load_texture("images/bonnie/sprite3.png"),
        ]
        self.walk_left_textures = [
            tex.flip_horizontally() for tex in self.walk_right_textures
        ]
        self.walk_up_textures = [
            arcade.load_texture("images/bonnie/sprite8.png"),
            arcade.load_texture("images/bonnie/sprite9.png"),
            arcade.load_texture("images/bonnie/sprite10.png"),
            arcade.load_texture("images/bonnie/sprite11.png"),
        ]
        self.walk_down_textures = [
            arcade.load_texture("images/bonnie/sprite4.png"),
            arcade.load_texture("images/bonnie/sprite5.png"),
            arcade.load_texture("images/bonnie/sprite6.png"),
            arcade.load_texture("images/bonnie/sprite7.png"),
        ]

        self.state = "inactive"
        self.texture = self.not_activate
        self.speed = 4
        self.chase_speed = 6
        self.stuck_timer = 0
        self.stuck_threshold = 0.5
        self.last_pos = (self.center_x, self.center_y)

        self.cur_texture_index = 0
        self.animation_time = 0.2
        self.patrol_animation_time = 0.25
        self.chase_animation_time = 0.1
        self.time_since_last_frame = 0
        self.facing_direction = 1

        self.patrol_timer = 0
        self.direction_change_interval = random.uniform(2.0, 5.0)

        self.last_dist_to_player = None
        self.stuck_path_timer = 0
        self.stuck_path_threshold = 0.5
        self.teleport_cooldown = 0

    def check_doors(self, doors_list: arcade.SpriteList, dt: float):
        """Проверяет столкновение с дверью и при необходимости телепортирует.

        :param doors_list: список спрайтов дверей
        :type doors_list: arcade.SpriteList
        :param dt: время с предыдущего кадра
        :type dt: float
        """
        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= dt
        if self.teleport_cooldown <= 0:
            door_hit = arcade.check_for_collision_with_list(self, doors_list)
            if door_hit:
                door = door_hit[0]
                orientation = door.properties.get("orientation", None)
                if orientation is not None:
                    if self.center_y < door.center_y:
                        self.center_y = door.center_y + door.height // 2 + self.height // 2 + 30
                    else:
                        self.center_y = door.center_y - door.height // 2 - self.height // 2 - 30
                else:
                    if self.center_x < door.center_x:
                        self.center_x = door.center_x + door.width // 2 + self.width // 2 + 30
                    else:
                        self.center_x = door.center_x - door.width // 2 - self.width // 2 - 30
                self.teleport_cooldown = 0.5

    def set_state(self, new_state):
        """Безопасно меняет состояние и обновляет скорость анимации.

        :param new_state: новое состояние ("inactive", "patrol", "chase")
        :type new_state: str
        """
        if self.state == new_state:
            return
        self.state = new_state
        if new_state == "chase":
            self.animation_time = self.chase_animation_time
        elif new_state == "patrol":
            self.animation_time = self.patrol_animation_time

    def update(self, dt: float, player: arcade.Sprite, stealth_mode: bool):
        """Обновляет логику движения в зависимости от состояния.

        :param dt: время с предыдущего кадра
        :type dt: float
        :param player: спрайт игрока
        :type player: arcade.Sprite
        :param stealth_mode: режим невидимости игрока
        :type stealth_mode: bool
        """
        if self.state == "chase" and stealth_mode:
            self.set_state("patrol")
            self.speed = 4
            self.patrol_timer = 0

        if self.state == "inactive":
            self.change_x = 0
            self.change_y = 0
            return

        if self.state != "chase":
            dist = arcade.get_distance_between_sprites(self, player)
            if dist < 400 and not stealth_mode:
                self.set_state("chase")
                self.speed = self.chase_speed

        if self.state == "patrol":
            self._patrol_update(dt)
            if self.change_x != 0 or self.change_y != 0:
                if abs(self.center_x - self.last_pos[0]) < 1 and abs(self.center_y - self.last_pos[1]) < 1:
                    self.stuck_timer += dt
                else:
                    self.stuck_timer = 0
                self.last_pos = (self.center_x, self.center_y)

                if self.stuck_timer > self.stuck_threshold:
                    angle = random.uniform(0, 2 * math.pi)
                    self.change_x = math.cos(angle) * self.speed
                    self.change_y = math.sin(angle) * self.speed
                    self.stuck_timer = 0
        elif self.state == "chase":
            if self.stuck_path_timer <= 0:
                self._chase_update(player)

            current_dist = arcade.get_distance_between_sprites(self, player)
            if self.last_dist_to_player is not None:
                if current_dist >= self.last_dist_to_player - 5:
                    self.stuck_path_timer += dt
                else:
                    self.stuck_path_timer = 0
            self.last_dist_to_player = current_dist

            if self.stuck_path_timer > self.stuck_path_threshold:
                dx = player.center_x - self.center_x
                dy = player.center_y - self.center_y
                dist = math.hypot(dx, dy)
                if dist > 0:
                    if random.random() < 0.5:
                        self.change_x = -dy / dist * self.speed
                        self.change_y = dx / dist * self.speed
                    else:
                        self.change_x = dy / dist * self.speed
                        self.change_y = -dx / dist * self.speed
                else:
                    angle = random.uniform(0, 2 * math.pi)
                    self.change_x = math.cos(angle) * self.speed
                    self.change_y = math.sin(angle) * self.speed
                self.stuck_path_timer = 0

    def _patrol_update(self, dt: float):
        """Случайное блуждание в режиме патруля.

        :param dt: время с предыдущего кадра
        :type dt: float
        """
        self.patrol_timer += dt
        if self.patrol_timer >= self.direction_change_interval:
            angle = random.uniform(0, 2 * math.pi)
            self.change_x = math.cos(angle) * self.speed
            self.change_y = math.sin(angle) * self.speed
            self.patrol_timer = 0
            self.direction_change_interval = random.uniform(2.0, 5.0)

    def _chase_update(self, player: arcade.Sprite):
        """Движение прямо к игроку в режиме погони.

        :param player: спрайт игрока
        :type player: arcade.Sprite
        """
        dx = player.center_x - self.center_x
        dy = player.center_y - self.center_y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.change_x = (dx / dist) * self.speed
            self.change_y = (dy / dist) * self.speed

    def update_animation(self, dt: float = 1 / 60):
        """Обновляет анимацию в зависимости от направления движения.

        :param dt: время с предыдущего кадра
        :type dt: float
        """
        self.time_since_last_frame += dt

        if self.change_x != 0:
            if self.change_x > 0:
                textures = self.walk_right_textures
                self.facing_direction = 1
            else:
                textures = self.walk_left_textures
                self.facing_direction = -1

            if self.time_since_last_frame >= self.animation_time:
                self.cur_texture_index = (self.cur_texture_index + 1) % len(textures)
                self.texture = textures[self.cur_texture_index]
                self.time_since_last_frame = 0

        elif self.change_y != 0:
            if self.change_y > 0:
                textures = self.walk_up_textures
            else:
                textures = self.walk_down_textures

            if self.time_since_last_frame >= self.animation_time:
                self.cur_texture_index = (self.cur_texture_index + 1) % len(textures)
                self.texture = textures[self.cur_texture_index]
                self.time_since_last_frame = 0

        else:
            if self.state == "inactive":
                self.texture = self.not_activate
            else:
                self.texture = self.idle_texture
            self.cur_texture_index = 0
            self.time_since_last_frame = 0


class Chika(arcade.Sprite):
    """Аниматроник Чика.

    При активации исчезает и появляется кекс, который перемещается.
    """

    def __init__(self):
        """Загружает текстуры, звук и инициализирует состояние."""
        super().__init__(scale=1.3)

        self.cupcake = arcade.load_texture('images/chika/cupcake.png')
        self.not_activate = arcade.load_texture('images/chika/sprite00.png')
        self.jumpscare_sound = arcade.load_sound('sounds/scearm_sound.mp3')
        self.jumpscare = arcade.load_texture('images/chika/jumpscare.jpg')

        self.state = "inactive"
        self.texture = self.not_activate
        self.alpha = 0


class Foxy(arcade.Sprite):
    """Аниматроник Фокси.

    Крадётся, меняя текстуры, затем атакует, если игрок не спрятался.
    """

    def __init__(self):
        """Загружает текстуры, звуки и задаёт начальные параметры."""
        super().__init__(scale=1.3)

        self.activated = False
        self.jumpscare = arcade.load_texture('images/foxy/jumpscare.jpg')
        self.jumpscare_sound = arcade.load_sound('sounds/scearm_sound.mp3')
        self.not_activate = arcade.load_texture('images/foxy/sprite00.png')
        self.idle_texture = arcade.load_texture("images/foxy/sprite4.png")
        self.walk_left_textures = [
            arcade.load_texture("images/foxy/sprite0.png"),
            arcade.load_texture("images/foxy/sprite1.png"),
            arcade.load_texture("images/foxy/sprite2.png"),
            arcade.load_texture("images/foxy/sprite3.png"),
        ]
        self.walk_right_textures = [
            tex.flip_horizontally() for tex in self.walk_left_textures
        ]
        self.walk_up_textures = [
            arcade.load_texture("images/foxy/sprite8.png"),
            arcade.load_texture("images/foxy/sprite9.png"),
            arcade.load_texture("images/foxy/sprite10.png"),
            arcade.load_texture("images/foxy/sprite11.png"),
        ]
        self.walk_down_textures = [
            arcade.load_texture("images/foxy/sprite4.png"),
            arcade.load_texture("images/foxy/sprite5.png"),
            arcade.load_texture("images/foxy/sprite6.png"),
            arcade.load_texture("images/foxy/sprite7.png"),
        ]

        self.state = "inactive"
        self.step_index = 0
        self.activation_timer = 0.0
        self.activation_interval = 20.0
        self.activation_chance = 0.6
        self.step_timer = 0.0
        self.step_interval = 25.0
        self.step_chance = 0.8
        self.chase_speed = 8
        self.facing_direction = 1

        self.texture = self.not_activate

        self.cur_texture_index = 0
        self.animation_time = 0.05
        self.time_since_last_frame = 0

        self.stuck_timer = 0
        self.stuck_threshold = 0.5
        self.last_pos = (self.center_x, self.center_y)

        self.last_dist_to_player = None
        self.stuck_path_timer = 0
        self.stuck_path_threshold = 1.0
        self.teleport_cooldown = 0

    def check_doors(self, doors_list: arcade.SpriteList, dt: float):
        """Проверяет столкновение с дверью и телепортирует при необходимости.

        :param doors_list: список спрайтов дверей
        :type doors_list: arcade.SpriteList
        :param dt: время с предыдущего кадра
        :type dt: float
        """
        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= dt
        if self.teleport_cooldown <= 0:
            door_hit = arcade.check_for_collision_with_list(self, doors_list)
            if door_hit:
                door = door_hit[0]
                orientation = door.properties.get("orientation", None)
                if orientation is not None:
                    if self.center_y < door.center_y:
                        self.center_y = door.center_y + door.height // 2 + self.height // 2 + 30
                    else:
                        self.center_y = door.center_y - door.height // 2 - self.height // 2 - 30
                else:
                    if self.center_x < door.center_x:
                        self.center_x = door.center_x + door.width // 2 + self.width // 2 + 30
                    else:
                        self.center_x = door.center_x - door.width // 2 - self.width // 2 - 30
                self.teleport_cooldown = 0.5

    def update(self, dt: float, player: arcade.Sprite, stealth_mode: bool):
        """Обновляет логику поведения: крадётся или преследует.

        :param dt: время с предыдущего кадра
        :type dt: float
        :param player: спрайт игрока
        :type player: arcade.Sprite
        :param stealth_mode: режим невидимости игрока
        :type stealth_mode: bool
        """
        if self.state == "inactive":
            self.activation_timer += dt
            if self.activation_timer >= self.activation_interval:
                self.activation_timer = 0
                if random.random() < self.activation_chance:
                    self.state = "stalking"
                    self.step_index = 0
                    self.texture = self.idle_texture

        elif self.state == "stalking":
            self.step_timer += dt
            if self.step_timer >= self.step_interval:
                self.step_timer = 0
                if random.random() < self.step_chance:
                    if self.step_index < 3:
                        self.step_index += 1
                        self.texture = self.walk_down_textures[self.step_index]
                    else:
                        if stealth_mode:
                            self.step_index = 0
                            self.texture = self.idle_texture
                        else:
                            self.state = "chasing"
                            self.center_y -= 200
                            self.speed = self.chase_speed
                            self._update_chase_direction(player)

        if self.state == "chasing":
            if self.stuck_path_timer <= 0:
                self._update_chase_direction(player)

            current_dist = arcade.get_distance_between_sprites(self, player)
            if self.last_dist_to_player is not None:
                if current_dist >= self.last_dist_to_player - 5:
                    self.stuck_path_timer += dt
                else:
                    self.stuck_path_timer = 0
            self.last_dist_to_player = current_dist

            if self.stuck_path_timer > self.stuck_path_threshold:
                dx = player.center_x - self.center_x
                dy = player.center_y - self.center_y
                dist = math.hypot(dx, dy)
                if dist > 0:
                    if random.random() < 0.5:
                        self.change_x = -dy / dist * self.speed
                        self.change_y = dx / dist * self.speed
                    else:
                        self.change_x = dy / dist * self.speed
                        self.change_y = -dx / dist * self.speed
                else:
                    angle = random.uniform(0, 2 * math.pi)
                    self.change_x = math.cos(angle) * self.speed
                    self.change_y = math.sin(angle) * self.speed
                self.stuck_path_timer = 0

    def _update_chase_direction(self, player: arcade.Sprite):
        """Устанавливает направление движения прямо к игроку.

        :param player: спрайт игрока
        :type player: arcade.Sprite
        """
        dx = player.center_x - self.center_x
        dy = player.center_y - self.center_y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.change_x = (dx / dist) * self.speed
            self.change_y = (dy / dist) * self.speed
        else:
            self.change_x = 0
            self.change_y = 0

    def update_animation(self, dt: float = 1 / 60):
        """Обновляет анимацию в зависимости от текущего состояния и движения.

        :param dt: время с предыдущего кадра
        :type dt: float
        """
        if self.state == "stalking":
            return

        self.time_since_last_frame += dt

        if self.change_x != 0:
            if self.change_x > 0:
                textures = self.walk_right_textures
                self.facing_direction = 1
            else:
                textures = self.walk_left_textures
                self.facing_direction = -1

            if self.time_since_last_frame >= self.animation_time:
                self.cur_texture_index = (self.cur_texture_index + 1) % len(textures)
                self.texture = textures[self.cur_texture_index]
                self.time_since_last_frame = 0

        elif self.change_y != 0:
            if self.change_y > 0:
                textures = self.walk_up_textures
            else:
                textures = self.walk_down_textures

            if self.time_since_last_frame >= self.animation_time:
                self.cur_texture_index = (self.cur_texture_index + 1) % len(textures)
                self.texture = textures[self.cur_texture_index]
                self.time_since_last_frame = 0

        else:
            if self.state == "inactive":
                self.texture = self.not_activate
            else:
                self.texture = self.idle_texture
            self.cur_texture_index = 0
            self.time_since_last_frame = 0
