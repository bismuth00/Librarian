import json
import flet as ft
from cosmos_exlibris import CosmosExlibris
from cosmos_inventory import CosmosInventory

class Cosmos(ft.Container):
    def __init__(self, page):
        super().__init__()
        self.books = json.load(open("books.json", "r", encoding="utf-8"))
        self.page = page

    def build(self):
        self.content = ft.Tabs(
            animation_duration=200,
            expand=True,
            is_secondary=True,
            tabs=[
                ft.Tab(
                    text="書籍情報",
                    icon=ft.Icons.MENU_BOOK,
                    content=CosmosExlibris(self.page, self.books)
                ),
                ft.Tab(
                    text="棚卸",
                    icon=ft.Icons.MOVE_DOWN,
                    content=CosmosInventory(self.page, self.books)
                ),
            ],
        )
