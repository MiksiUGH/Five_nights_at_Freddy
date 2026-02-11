from arcade import Window, run
from views import Game, MainMenu, StaticMenu


class MainWindow(Window):
    def __init__(self, width: int, height: int, title: str) -> None:
        super().__init__(width, height, title)

        self.main_menu: MainMenu = MainMenu()
        self.game: Game
        self.static_menu: StaticMenu

    def setup(self) -> None:
        self.show_view(self.main_menu)

    def on_update(self, delta_time: float) -> None:
        ...

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        ...


if __name__ == "__main__":
    window = MainWindow(800, 600, "Five Nights at Freddy's")
    window.setup()
    run()
