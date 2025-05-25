import flet as ft
import time
import util

class Test(ft.Container):
    def __init__(self, page):
        super().__init__()
        self.page = page

    def build(self):
        self.categories_detail = ft.Dropdown(label="カテゴリ", value="0")
        self.categories_detail.options.append(ft.dropdown.Option(key=0, text="未設定(188)"))
        self.categories_detail.options.append(ft.dropdown.Option(key=1, text="20F本棚F-6(0)"))
        content = ft.Column(controls=[
            ft.Text("キーボードを押してみてください"),
            self.categories_detail,
            ft.FilledButton("カメラ", col=1, icon=ft.Icons.COPY, on_click=lambda e: self.update_cat()),
        ])
        
        self.content = ft.Tabs(
            is_secondary=True,
            animation_duration=200,
            expand=True,
            tabs=[
                ft.Tab(
                    text="私物漫画管理",
                    icon=ft.Icons.BOOK,
                    content=content,
                ),
                ft.Tab(
                    text="会社資料管理",
                    icon=ft.Icons.BUSINESS,
                    content=ft.Text(f"ttttttttt"),
                )
            ])
    def update_cat(self):
        self.categories_detail.options.clear()
        self.categories_detail.options.append(ft.dropdown.Option(key=0, text="未設定(187)"))
        self.categories_detail.options.append(ft.dropdown.Option(key=1, text="20F本棚F-6(1)"))
        self.categories_detail.options.append(ft.dropdown.Option(key=len(self.categories_detail.options), text=f"len={len(self.categories_detail.options)}"))
        self.page.update()


def main(page: ft.Page):

    test = Test(page)
    tabs = ft.Tabs(
        animation_duration=200,
        expand=True,
        tabs=[
            ft.Tab(
                text="私物漫画管理",
                icon=ft.Icons.BOOK,
                content=test,
            ),
            ft.Tab(
                text="会社資料管理",
                icon=ft.Icons.BUSINESS,
                content=ft.Text(f"ttttttttt"),
            )
        ])

    page.add(tabs)
    
    dialog_wait = ft.AlertDialog(
        modal=True,
        title=ft.Text(""))

    def on_key(e):
        with util.OpenDialog(page, dialog_wait, "処理中…"):
            print(f"key: {e.key}")
            test.update_cat()
            # categories_detail = ft.Dropdown(label="カテゴリ", value="0")
            # categories_detail.options.append(ft.dropdown.Option(key=0, text="未設定(187)"))
            # categories_detail.options.append(ft.dropdown.Option(key=1, text="20F本棚F-6(1)"))
            # categories_detail.value = 99999
            page.update()
            time.sleep(1)
        # categories_detail.options.pop()
        # categories_detail.value = 0
        # page.update()

    page.on_keyboard_event = on_key
    page.update()

ft.app(target=main)
