"""Главный модуль окна приложения.

Запускает игру, устанавливает главное меню.
"""


from arcade import Window, run
from views import MainMenu


class MainWindow(Window):
    """Основное окно игры, содержит виды (экраны)."""

    def __init__(self, width: int, height: int, title: str) -> None:
        """Создаёт окно с заданными размерами и заголовком."""
        super().__init__(width, height, title)
        self.main_menu: MainMenu = MainMenu()

    def setup(self) -> None:
        """Устанавливает начальный вид — главное меню."""
        self.show_view(self.main_menu)


if __name__ == "__main__":
    window = MainWindow(1550, 850, "Five Nights at Freddy's")
    window.setup()
    run()
