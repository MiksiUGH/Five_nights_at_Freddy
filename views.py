from arcade import View
import arcade
from arcade.gui import UIManager, UIBoxLayout, UIFlatButton, UIAnchorLayout


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

        self.map = arcade.load_tilemap('maps/fnaf.tmx')

    def on_show(self):
        ...

    def on_draw(self):
        self.clear()
        arcade.draw_text("Game View — здесь будет игра",
                         self.window.width // 2, self.window.height // 2,
                         arcade.color.WHITE, anchor_x="center")

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            self.window.show_view(PauseMenu(self))
        return None


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


class PauseMenu(View):
    def __init__(self, game):
        super().__init__()
        self.game = game

        self.manager = UIManager()
        # НЕ включаем здесь – включим в on_show

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
        """При показе паузы включаем UI и мышь."""
        self.manager.enable()
        self.window.set_mouse_visible(True)

    def on_hide(self):
        """При скрытии паузы отключаем UI."""
        self.manager.disable()

    def on_draw(self):
        """Отрисовка: игра + затемнение + UI."""
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
