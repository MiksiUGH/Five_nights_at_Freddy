from arcade import View, PhysicsEngineSimple, Camera2D
import arcade, time, random
from arcade.gui import UIManager, UIBoxLayout, UIFlatButton, UIAnchorLayout
from charecters import NightGuard, Bonnie, Freddy, Chika, Foxy


class MainMenu(View):
    def __init__(self):
        super().__init__()

        try:
            self.background = arcade.load_texture("images/background.png")
        except FileNotFoundError:
            self.background = arcade.color.BLACK

        self.manager = UIManager()
        self.manager.enable()

        v_box = UIBoxLayout(vertical=True, space_between=20)

        play_button = UIFlatButton(text="Играть", width=250, height=60)
        play_button.on_click = self.on_click_play
        v_box.add(play_button)

        stats_button = UIFlatButton(text="Посмотреть статистику", width=350, height=60)
        stats_button.on_click = self.on_click_stats
        v_box.add(stats_button)

        anchor_layout = UIAnchorLayout()
        anchor_layout.add(v_box, anchor_x="center_x", anchor_y="center_y")
        self.manager.add(anchor_layout)

        self.buttons = [play_button, stats_button]
        self.selected_index = 0
        self._update_selection()

    def on_show(self):
        """Вызывается при показе вида."""
        self.manager.enable()
        self.window.set_mouse_visible(True)

    def on_hide(self):
        """Вызывается при скрытии вида."""
        self.manager.disable()

    def on_draw(self):
        """Отрисовка."""
        self.clear()
        arcade.draw_texture_rect(self.background,
                                 arcade.rect.XYWH(self.width // 2, self.height // 2, self.width, self.height))
        self.manager.draw()

    def on_click_play(self, event):
        self.window.show_view(Game())

    def on_click_stats(self, event):
        self.window.show_view(StaticMenu())

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.UP:
            self.selected_index = (self.selected_index - 1) % len(self.buttons)
            self._update_selection()
        elif symbol == arcade.key.DOWN:
            self.selected_index = (self.selected_index + 1) % len(self.buttons)
            self._update_selection()
        elif symbol == arcade.key.ENTER:
            if self.selected_index == 0:
                self.on_click_play(None)
            else:
                self.on_click_stats(None)

    def _update_selection(self):
        """Визуально выделяем выбранную кнопку."""
        for i, btn in enumerate(self.buttons):
            if i == self.selected_index:
                btn.color = arcade.color.LIGHT_BLUE
                btn.hover_color = arcade.color.LIGHT_BLUE
                btn.press_color = arcade.color.BRIGHT_GREEN
            else:
                btn.color = None
                btn.hover_color = None
                btn.press_color = None


class Game(View):
    def __init__(self):
        super().__init__()
        self.scene = None
        self.map = None
        self.wall_list = None
        self.physics_engine = None
        self.stealth_mode = False
        self.start_time = None
        self.game_over = False
        self.game_over_timer = 0
        self.game_over_duration = 2.0

        self.map = arcade.load_tilemap("maps/fnaf.tmx", scaling=3.7)
        self.scene = arcade.Scene.from_tilemap(self.map)
        self.world_width = self.map.width * self.map.tile_width * 3.7
        self.world_height = self.map.height * self.map.tile_height * 3.7

        self.player = NightGuard()
        self.player_list = arcade.SpriteList()
        self.player.center_x = 400
        self.player.center_y = 300

        self.player_list.append(self.player)
        self.wall_list = self.map.sprite_lists["walls"]
        self.doors_list = self.map.sprite_lists["doors"]
        self.objects_list = self.map.sprite_lists["objects"]
        self.textures_list = self.map.sprite_lists["textures"]

        self.physics_engine = PhysicsEngineSimple(self.player, (self.wall_list, self.doors_list))

        self.world_camera = Camera2D()
        self.gui_camera = Camera2D()
        self.center_camera_on_player()

        self.bonnie_list = arcade.SpriteList()
        self.bonnie_physics = None
        self.activation_timer = 0
        self.activation_interval = 10.0  # каждые 10 секунд

        # Создаём Бонни и добавляем в список
        self.bonnie = Bonnie()
        # Установим начальную позицию (подбери координаты, где Бонни должен появиться)
        self.bonnie.center_x = 2100
        self.bonnie.center_y = 2330
        self.bonnie_list.append(self.bonnie)

        self.chika = Chika()
        self.chika.center_x = 1700  # координаты сцены
        self.chika.center_y = 2330
        self.chika_list = arcade.SpriteList()
        self.chika_list.append(self.chika)

        # Кекс
        self.cupcake_sprite = arcade.Sprite(self.chika.cupcake, scale=0.05)
        self.cupcake_sprite.alpha = 0
        self.cupcake_list = arcade.SpriteList()
        self.cupcake_list.append(self.cupcake_sprite)

        self.chika_activation_timer = 0
        self.chika_activation_interval = 15.0
        self.chika_activated = False

        self.cupcake_timer = 0
        self.cupcake_interval = 15.0

        # Физика для Бонни (те же стены)
        self.bonnie_physics = PhysicsEngineSimple(self.bonnie, (self.wall_list, self.cupcake_list))

    def on_show_view(self):
        self.start_time = time.time()
        self.activation_timer = 0
        self.bonnie.last_pos = (self.bonnie.center_x, self.bonnie.center_y)
        self.game_over = False
        self.chika_activation_timer = 0
        self.chika_activated = False
        self.chika.alpha = 255
        self.chika.texture = self.chika.not_activate
        self.cupcake_sprite.alpha = 0
        self.cupcake_timer = 0

    def _place_cupcake_randomly(self):
        """Размещает кекс в случайной позиции, не занятой стенами."""
        for _ in range(100):  # максимум 100 попыток
            x = random.uniform(42, self.world_width - 42)
            y = random.uniform(42, self.world_height - 42)
            self.cupcake_sprite.position = (x, y)
            if not arcade.check_for_collision_with_list(self.cupcake_sprite, self.wall_list):
                if not arcade.check_for_collision_with_list(self.cupcake_sprite, self.doors_list):
                    if arcade.check_for_collision_with_list(self.cupcake_sprite, self.textures_list):
                        return

        x = random.uniform(50, self.world_width - 50)
        y = random.uniform(50, self.world_height - 50)
        self.cupcake_sprite.position = (x, y)

    def center_camera_on_player(self):
        """Перемещает мировую камеру так, чтобы игрок был в центре экрана,
        с учётом границ карты."""
        dead_zone_h = int(self.window.height * 0.45)
        dead_zone_w = int(self.window.width * 0.35)
        camera_lerp = 1.1
        self.world_width = int(self.map.width * self.map.tile_width * 3.7)
        self.world_height = int(self.map.height * self.map.tile_height * 3.7)

        cam_x, cam_y = self.world_camera.position
        dz_left = cam_x - dead_zone_w // 2
        dz_right = cam_x + dead_zone_w // 2
        dz_bottom = cam_y - dead_zone_h // 2
        dz_top = cam_y + dead_zone_h // 2

        px, py = self.player.center_x, self.player.center_y
        target_x, target_y = cam_x, cam_y

        if px < dz_left:
            target_x = px + dead_zone_w // 2
        elif px > dz_right:
            target_x = px - dead_zone_w // 2
        if py < dz_bottom:
            target_y = py + dead_zone_h // 2
        elif py > dz_top:
            target_y = py - dead_zone_h // 2

        half_w = self.world_camera.viewport_width / 2
        half_h = self.world_camera.viewport_height / 2
        target_x = max(half_w, min(self.world_width - half_w, target_x))
        target_y = max(half_h, min(self.world_height - half_h, target_y))

        smooth_x = (1 - camera_lerp) * cam_x + camera_lerp * target_x
        smooth_y = (1 - camera_lerp) * cam_y + camera_lerp * target_y
        self.cam_target = (smooth_x, smooth_y)

        self.world_camera.position = (self.cam_target[0], self.cam_target[1])

    def on_draw(self):
        self.clear()

        self.world_camera.use()
        if self.scene:
            self.scene.draw()
        self.player_list.draw()
        self.bonnie_list.draw()
        self.chika_list.draw()  # Чика видна, пока alpha=255
        if self.chika_activated:
            self.cupcake_list.draw()

        self.gui_camera.use()

        if self.start_time and not self.game_over:
            elapsed = time.time() - self.start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            time_str = f"{minutes:02d}:{seconds:02d}"
            arcade.draw_text(
                time_str,
                self.window.width - 20,  # отступ справа
                self.window.height - 20,  # отступ сверху
                arcade.color.WHITE,
                font_size=20,
                anchor_x="right",
                anchor_y="top"
            )

        if self.game_over:
            texture = None
            if arcade.check_for_collision_with_list(self.player, self.bonnie_list):
                texture = self.bonnie.jumpscare
            elif arcade.check_for_collision_with_list(self.player, self.cupcake_list):
                texture = self.chika.jumpscare

            arcade.draw_texture_rect(
                texture, arcade.LBWH(0, 0, self.width, self.height),
            )

    def on_update(self, dt: float):
        if self.game_over:
            self.game_over_timer += dt
            if self.game_over_timer >= self.game_over_duration:
                self.window.show_view(MainMenu())
            return

        self.physics_engine.update()
        self.player.update_animation(dt)
        self.center_camera_on_player()

        if self.bonnie_physics:
            self.bonnie_physics.update()  # применяем физику к Бонни
        self.bonnie.update(dt, self.player, self.stealth_mode)
        self.bonnie.update_animation(dt)

        # Проверка столкновения Бонни с игроком
        if not self.stealth_mode and arcade.check_for_collision(self.player, self.bonnie):
            self.game_over = True
            self.game_over_timer = 0
            arcade.play_sound(self.bonnie.jumpscare_sound)
            self.player.change_x = 0
            self.player.change_y = 0
            self.bonnie.change_x = 0
            self.bonnie.change_y = 0
            print("Bonnie caught you! Game Over")

        # Таймер активации Бонни (каждые 10 секунд)
        self.activation_timer += dt
        if self.activation_timer >= self.activation_interval:
            self.activation_timer = 0
            if self.bonnie.state == "inactive":
                if random.random() < 0.8:  # 80% шанс
                    self.bonnie.state = "patrol"
                    self.bonnie.texture = self.bonnie.idle_texture
                    self.bonnie.center_y = 2250
                    print("Bonnie activated!")

        if not self.chika_activated:
            self.chika_activation_timer += dt
            if self.chika_activation_timer >= self.chika_activation_interval:
                self.chika_activation_timer = 0
                if random.random() < 0.7:
                    self.chika_activated = True
                    self.chika.alpha = 0  # Чика исчезает
                    self.cupcake_sprite.alpha = 255
                    self._place_cupcake_randomly()
                    print("Chika activated, cupcake spawned!")
        else:
            self.cupcake_timer += dt
            if self.cupcake_timer >= self.cupcake_interval:
                self.cupcake_timer = 0
                self._place_cupcake_randomly()
                print("Cupcake moved")

            # Проверка столкновения с кексом
        if self.chika_activated and not self.stealth_mode:
            if arcade.check_for_collision(self.player, self.cupcake_sprite):
                self.game_over = True
                self.game_over_timer = 0
                arcade.play_sound(self.chika.jumpscare_sound)
                self.player.change_x = 0
                self.player.change_y = 0
                print("Cupcake caught you!")

    def on_key_press(self, symbol: int, modifiers: int):
        if self.game_over:
            return
        if not self.stealth_mode:
            if symbol == arcade.key.W:
                self.player.change_y = self.player.speed
            if symbol == arcade.key.S:
                self.player.change_y = -self.player.speed
            if symbol == arcade.key.A:
                self.player.change_x = -self.player.speed
            if symbol == arcade.key.D:
                self.player.change_x = self.player.speed

        if symbol == arcade.key.SPACE:
            activation_distance = 110
            for obj in self.objects_list:
                dist = arcade.get_distance_between_sprites(self.player, obj)
                if dist <= activation_distance:
                    self.stealth_mode = True
                    self.player.alpha = 0
                    self.player.change_x = 0
                    self.player.change_y = 0
                    break

    def on_key_release(self, symbol: int, modifiers: int):
        if self.game_over:
            return
        if symbol == arcade.key.ESCAPE:
            self.window.show_view(PauseMenu(self))
        if symbol == arcade.key.W or symbol == arcade.key.S:
            self.player.change_y = 0
        if symbol == arcade.key.A or symbol == arcade.key.D:
            self.player.change_x = 0
        if symbol == arcade.key.E:
            activation_distance = 110
            for door in self.doors_list:
                dist = arcade.get_distance_between_sprites(self.player, door)
                if dist <= activation_distance:
                    orientation = door.properties.get("orientation", None)
                    if orientation is not None:
                        if self.player.center_y < door.center_y:
                            self.player.center_y = door.center_y + door.height // 2 + self.player.height // 2 + 30
                        else:
                            self.player.center_y = door.center_y - door.height // 2 - self.player.height // 2 - 30
                    else:
                        if self.player.center_x < door.center_x:
                            self.player.center_x = door.center_x + door.width // 2 + self.player.width // 2 + 30
                        else:
                            self.player.center_x = door.center_x - door.width // 2 - self.player.width // 2 - 30
                    break
        if symbol == arcade.key.SPACE:
            self.stealth_mode = False
            self.player.alpha = 255


class PauseMenu(View):
    def __init__(self, game):
        super().__init__()
        self.ui_camera = None
        self.game = game

        self.manager = UIManager()

        v_box = UIBoxLayout(vertical=True, space_between=20)

        resume_btn = UIFlatButton(text="Продолжить", width=300, height=60)
        resume_btn.on_click = self.on_resume
        v_box.add(resume_btn)

        main_menu_btn = UIFlatButton(text="Главное меню", width=300, height=60)
        main_menu_btn.on_click = self.on_main_menu
        v_box.add(main_menu_btn)

        quit_btn = UIFlatButton(text="Выход", width=300, height=60)
        quit_btn.on_click = self.on_quit
        v_box.add(quit_btn)

        anchor = UIAnchorLayout()
        anchor.add(v_box, anchor_x="center_x", anchor_y="center_y")
        self.manager.add(anchor)

        self.buttons = [resume_btn, main_menu_btn, quit_btn]
        self.selected_index = 0
        self._update_selection()

    def on_show(self):
        self.manager.enable()
        self.window.set_mouse_visible(True)

    def on_hide(self):
        self.manager.disable()

    def on_draw(self):
        self.game.on_draw()
        self.manager.draw()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        self.manager.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        self.manager.on_mouse_release(x, y, button, modifiers)

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.manager.on_mouse_motion(x, y, dx, dy)

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.UP:
            self.selected_index = (self.selected_index - 1) % len(self.buttons)
            self._update_selection()
        elif symbol == arcade.key.DOWN:
            self.selected_index = (self.selected_index + 1) % len(self.buttons)
            self._update_selection()
        elif symbol == arcade.key.ENTER:
            self.buttons[self.selected_index].on_click(None)
        elif symbol == arcade.key.ESCAPE:
            self.window.show_view(self.game)

    def on_resume(self, event):
        self.window.show_view(self.game)

    def on_main_menu(self, event):
        self.window.show_view(MainMenu())

    def on_quit(self, event):
        self.window.close()

    def _update_selection(self):
        for i, btn in enumerate(self.buttons):
            if i == self.selected_index:
                btn.color = arcade.color.LIGHT_BLUE
                btn.hover_color = arcade.color.LIGHT_BLUE
                btn.press_color = arcade.color.BRIGHT_GREEN
            else:
                btn.color = None
                btn.hover_color = None
                btn.press_color = None
            btn.trigger_render()


class StaticMenu(View):
    def on_show(self):
        self.background_color = arcade.color.DARK_GREEN

    def on_draw(self):
        self.clear()
        arcade.draw_text("Statistics Menu — здесь будет статистика",
                         self.window.width // 2, self.window.height // 2,
                         arcade.color.WHITE, anchor_x="center")

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            self.window.show_view(MainMenu())
        return None
