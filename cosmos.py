import json
import re
import subprocess
import time
import flet as ft
import util

class Cosmos(ft.Container):
    def __init__(self, page, dialog_wait, dialog_error):
        super().__init__()
        self.books = json.load(open("books.json", "r", encoding="utf-8"))
        self.page = page
        self.dialog_wait = dialog_wait
        self.dialog_error = dialog_error

    def did_mount(self):
        def shelf_keyboard(e):
            if e.key == "Escape":
                self.buttons.selected_index = (self.buttons.selected_index + 1) % len(self.buttons.controls)
                self.buttons.update()
        self.page.on_keyboard_event = shelf_keyboard
        self.page.update()

    def build(self):
        self.buttons = ft.CupertinoSlidingSegmentedButton(
            selected_index=0,
            controls=[
                ft.Text("無印"),
                ft.Text("ＢＫ"),
                ft.Text("ＣＤ"),
                ft.Text("ＤＶ"),
                ft.Text("ＨＶ"),
                ft.Text("ISBN"),
            ]
        )

        def shelf_change(e):
            text = []
            for book in self.books.values():
                ids = book['class_id'].split("-")
                if len(ids) > 1 and not ids[0].isdecimal():
                    id = ids[1]
                else:
                    id = ids[0]
                if id == e.data:
                    print(book)
                    text.append("管理番号:{} タイトル:{}".format(book['class_id'], book['title']))
            if len(text) > 0:
                print(text)
                snackbar = ft.SnackBar(ft.Text("\n".join(text)))
                self.page.add(snackbar)
                self.page.overlay.append(snackbar)
                snackbar.open = True
                self.page.update()    

        self.shelf_text = ft.TextField(label="管理番号 or ISBN", on_change=shelf_change)
        self.inventory_text = ft.TextField(label="管理番号 or ISBN", min_lines=1, max_lines=5)

        self.shelf_table = ft.DataTable(
            sort_column_index=1,
            columns = [
                ft.DataColumn(ft.Text("")),
                ft.DataColumn(ft.Text("管理番号")),
                ft.DataColumn(ft.Text("カテゴリ")),
                ft.DataColumn(ft.Text("書名")),
                ft.DataColumn(ft.Text("場所")),
            ],
        )

        self.inventory_table = ft.DataTable(
                    columns = [
                        ft.DataColumn(ft.Text("")),
                        ft.DataColumn(ft.Text("管理番号")),
                        ft.DataColumn(ft.Text("書名")),
                        ft.DataColumn(ft.Text("状態")),
                    ],
                )
        # for _, book in self.books.items():
        #     self.shelf_table.rows.append(
        #         ft.DataRow(
        #             cells = [
        #                 ft.DataCell(ft.Text(len(self.shelf_table.rows) + 1, selectable=True)),
        #                 ft.DataCell(ft.Text(book["class_id"], selectable=True)),
        #                 ft.DataCell(ft.Text(book["category"], selectable=True)),
        #                 ft.DataCell(ft.Text(book["title"], selectable=True)),
        #                 ft.DataCell(ft.Text(book.get("location"), selectable=True)),
        #             ]
        #         )
        #     )

        self.content = ft.Tabs(
            animation_duration=200,
            expand=True,
            is_secondary=True,
            tabs=[
                ft.Tab(
                    text="書籍情報",
                    icon=ft.Icons.MENU_BOOK,
                    content=ft.Column(controls=[
                        ft.Divider(color=ft.Colors.TRANSPARENT),
                        ft.ResponsiveRow([
                            ft.Text("管理カテゴリ", col=1, theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                            ft.Column(col=3, controls=[self.buttons]),
                            ft.Column(col=8, controls=[self.shelf_text]),
                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Column(controls=[self.shelf_table], scroll=ft.ScrollMode.AUTO, expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
                    ])
                ),
                ft.Tab(
                    text="棚卸",
                    icon=ft.Icons.MOVE_DOWN,
                    content=ft.Column(controls=[
                            ft.Divider(color=ft.Colors.TRANSPARENT),
                            ft.ResponsiveRow([
                                ft.Column(col=8, controls=[]),
                                ft.FilledButton("データ取得", col=2, icon=ft.Icons.DOWNLOAD),
                                ft.FilledButton("棚卸終了", col=2, icon=ft.Icons.PIN_END)
                            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            self.inventory_text,
                            ft.Divider(),
                            ft.Column(controls=[self.inventory_table], scroll=ft.ScrollMode.AUTO, expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
                    ]),
                )
            ]
        )

