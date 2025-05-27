import flet as ft
import util
from booklog_shelf import BooklogShelf
from booklog_location import BooklogLocation
from booklog_inventory import BooklogInventory


class Booklog(ft.Container):
    def __init__(self, page, config):
        super().__init__()
        self.page = page
        self.config = config

    def build(self):
        self.driver = util.login_booklog(self.config)
        self.categories = util.get_book_categories(self.driver, self.config)
        self.content = ft.Tabs(
            animation_duration=200,
            expand=True,
            is_secondary=True,
            tabs=[
                ft.Tab(
                    text="書籍情報",
                    icon=ft.Icons.MENU_BOOK,
                    content=BooklogShelf(self.page, self.driver),
                ),
                ft.Tab(
                    text="カテゴリ変更",
                    icon=ft.Icons.LIBRARY_BOOKS,
                    content=BooklogLocation(self.page, self.driver, self.categories),
                ),
                ft.Tab(
                    text="棚卸",
                    icon=ft.Icons.MOVE_DOWN,
                    content=BooklogInventory(
                        self.page, self.driver, self.categories, self.config
                    ),
                ),
            ],
        )
