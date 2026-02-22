import arcade, math, random


class NightGuard(arcade.Sprite):
    def __init__(self):
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
        """Обновление анимации в зависимости от движения."""
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
    ...


class Bonnie(arcade.Sprite):
    def __init__(self):
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

        # Начинаем в неактивном состоянии
        self.state = "inactive"  # inactive, patrol, chase
        self.texture = self.not_activate
        self.speed = 4
        self.chase_speed = 6
        self.stuck_timer = 0
        self.stuck_threshold = 0.5  # секунд без движения
        self.last_pos = (self.center_x, self.center_y)

        # Для анимации
        self.cur_texture_index = 0
        self.animation_time = 0.2
        self.time_since_last_frame = 0
        self.facing_direction = 1

        # Таймеры для смены направления в патруле
        self.patrol_timer = 0
        self.direction_change_interval = random.uniform(2.0, 5.0)  # секунд

    def update(self, dt: float, player: arcade.Sprite, stealth_mode: bool):
        # Если в погоне и игрок в невидимости — теряем цель и возвращаемся к патрулю
        if self.state == "chase" and stealth_mode:
            self.state = "patrol"
            self.speed = 4  # исходная скорость патруля
            self.patrol_timer = 0  # сбросим таймер, чтобы он сразу выбрал направление

        # Если неактивен — ничего не делаем
        if self.state == "inactive":
            self.change_x = 0
            self.change_y = 0
            return

        # Проверка видимости игрока для перехода в погоню (только если не в погоне и игрок видим)
        if self.state != "chase":
            dist = arcade.get_distance_between_sprites(self, player)
            if dist < 400 and not stealth_mode:
                self.state = "chase"
                self.speed = self.chase_speed
                # Сброс патрульного таймера (не нужен в погоне)

        # Обработка текущего состояния
        if self.state == "patrol":
            self._patrol_update(dt)
        elif self.state == "chase":
            self._chase_update(player)

        if (self.change_x != 0 or self.change_y != 0) and self.state != "inactive":
            if abs(self.center_x - self.last_pos[0]) < 1 and abs(self.center_y - self.last_pos[1]) < 1:
                self.stuck_timer += dt
            else:
                self.stuck_timer = 0
            self.last_pos = (self.center_x, self.center_y)

            if self.stuck_timer > self.stuck_threshold:
                # Застрял — меняем направление
                if self.state == "patrol":
                    angle = random.uniform(0, 2 * math.pi)
                    self.change_x = math.cos(angle) * self.speed
                    self.change_y = math.sin(angle) * self.speed
                elif self.state == "chase":
                    dx = player.center_x - self.center_x
                    dy = player.center_y - self.center_y
                    dist = math.hypot(dx, dy)
                    if dist > 0:
                        if random.random() < 0.5:
                            # влево
                            self.change_x = -dy / dist * self.speed
                            self.change_y = dx / dist * self.speed
                        else:
                            # вправо
                            self.change_x = dy / dist * self.speed
                            self.change_y = -dx / dist * self.speed
                    else:
                        angle = random.uniform(0, 2 * math.pi)
                        self.change_x = math.cos(angle) * self.speed
                        self.change_y = math.sin(angle) * self.speed
                self.stuck_timer = 0

    def _patrol_update(self, dt: float):
        """Случайное блуждание."""
        self.patrol_timer += dt
        if self.patrol_timer >= self.direction_change_interval:
            # Выбираем новое направление
            angle = random.uniform(0, 2 * math.pi)
            self.change_x = math.cos(angle) * self.speed
            self.change_y = math.sin(angle) * self.speed
            self.patrol_timer = 0
            self.direction_change_interval = random.uniform(2.0, 5.0)

    def _chase_update(self, player: arcade.Sprite):
        """Бежим прямо к игроку."""
        dx = player.center_x - self.center_x
        dy = player.center_y - self.center_y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.change_x = (dx / dist) * self.speed
            self.change_y = (dy / dist) * self.speed

    def update_animation(self, dt: float = 1 / 60):
        """Обновление анимации в зависимости от движения (как у игрока)."""
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
            # В состоянии покоя используем idle_texture, если активен, иначе not_activate
            if self.state == "inactive":
                self.texture = self.not_activate
            else:
                self.texture = self.idle_texture
            self.cur_texture_index = 0
            self.time_since_last_frame = 0


class Chika(arcade.Sprite):
    def __init__(self):
        super().__init__(scale=1.3)

        self.cupcake = arcade.load_texture('images/chika/cupcake.png')
        self.not_activate = arcade.load_texture('images/chika/sprite00.png')
        self.jumpscare_sound = arcade.load_sound('sounds/scearm_sound.mp3')
        self.jumpscare = arcade.load_texture('images/chika/jumpscare.jpg')

        self.state = "inactive"  # inactive, active
        self.texture = self.not_activate
        self.alpha = 255


class Foxy(arcade.Sprite):
    def __init__(self):
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

        self.state = "inactive"  # inactive, stalking, chasing
        self.step_index = 0  # 0..3 (sprite4..sprite7)
        self.activation_timer = 0.0
        self.activation_interval = 20.0
        self.activation_chance = 0.6
        self.step_timer = 0.0
        self.step_interval = 25.0
        self.step_chance = 0.5
        self.chase_speed = 8  # скорость в погоне
        self.facing_direction = 1

        # Начальная текстура
        self.texture = self.not_activate

        # Для анимации (как у Bonnie)
        self.cur_texture_index = 0
        self.animation_time = 0.2
        self.time_since_last_frame = 0

    def update(self, dt: float, player: arcade.Sprite, stealth_mode: bool):
        """Обновление логики Foxy."""
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
                    else:  # step_index == 3 (sprite7)
                        if stealth_mode:
                            # Откат, если игрок спрятался
                            self.step_index = 0
                            self.texture = self.idle_texture
                        else:
                            # Атака
                            self.state = "chasing"
                            self.center_y -= 5  # опускаемся
                            self.speed = self.chase_speed
                            self._update_chase_direction(player)

        elif self.state == "chasing":
            self._update_chase_direction(player)

    def _update_chase_direction(self, player: arcade.Sprite):
        """Направление к игроку для погони."""
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
        """Обновление анимации (для chasing работает как у Bonnie, для stalking не меняет текстуру)."""
        if self.state == "stalking":
            # В stalking текстура управляется вручную через step_index
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


class Springtrap(arcade.Sprite):
    ...


class ShuteredFreddy(arcade.Sprite):
    ...
