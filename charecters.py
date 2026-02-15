import arcade


class NightGuard(arcade.Sprite):
    def __init__(self):
        super().__init__(scale=1.3)

        # Загрузка текстур (проверь пути и расширения)
        self.idle_texture = arcade.load_texture("images/player/sprite0.png")
        self.walk_right_textures = [
            arcade.load_texture("images/player/sprite1.jpg"),
            arcade.load_texture("images/player/sprite2.png"),
            arcade.load_texture("images/player/sprite3.jpg"),
        ]
        self.walk_left_textures = [
            tex.flip_horizontally() for tex in self.walk_right_textures
        ]

        # Текущее состояние
        self.texture = self.idle_texture
        self.speed = 5

        # Для анимации
        self.cur_texture_index = 0
        self.animation_time = 0.15       # секунд на кадр
        self.time_since_last_frame = 0
        self.facing_direction = 1           # 1 - вправо, -1 - влево

    def update_animation(self, dt: float = 1 / 60):
        """Обновление анимации в зависимости от движения."""
        if self.change_x != 0 or self.change_y != 0:
            # Определяем направление по горизонтали
            if self.change_x > 0:
                self.facing_direction = 1
            elif self.change_x < 0:
                self.facing_direction = -1

            # Выбираем текстуры для текущего направления
            if self.facing_direction == 1:
                textures = self.walk_right_textures
            else:
                textures = self.walk_left_textures

            # Переключаем кадр по времени
            self.time_since_last_frame += dt
            if self.time_since_last_frame >= self.animation_time:
                self.cur_texture_index = (self.cur_texture_index + 1) % len(textures)
                self.texture = textures[self.cur_texture_index]
                self.time_since_last_frame = 0
        else:
            # Не движется – ставим idle
            self.texture = self.idle_texture
            self.cur_texture_index = 0
            self.time_since_last_frame = 0
