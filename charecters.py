import arcade

class NightGuard(arcade.Sprite):
    def __init__(self):
        super().__init__(scale=1.3)

        self.idle_texture = arcade.load_texture("images/player/sprite4.png")
        self.walk_right_textures = [
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
