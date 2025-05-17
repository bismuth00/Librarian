import json
import re
import subprocess
import time
import flet as ft
import util

class Cosmos(ft.Container):
    def __init__(self, page, dialog_wait, dialog_error):
        super().__init__()
        self.books = json.load(open("cosmos.json", "r", encoding="utf-8"))
        self.page = page
        self.dialog_wait = dialog_wait
        self.dialog_error = dialog_error

    def build(self):
        shelf_table = ft.DataTable(
            sort_column_index=1,
            columns = [
                ft.DataColumn(ft.Text("")),
                ft.DataColumn(ft.Text("管理番号")),
                ft.DataColumn(ft.Text("カテゴリ")),
                ft.DataColumn(ft.Text("書名")),
                ft.DataColumn(ft.Text("場所")),
            ],
        )
        for book in self.books:
            shelf_table.rows.append(
                ft.DataRow(
                    cells = [
                        ft.DataCell(ft.Text(len(shelf_table.rows) + 1, selectable=True)),
                        ft.DataCell(ft.Text(book["text-no-wrap (2)"], selectable=True)),
                        ft.DataCell(ft.Text(book["v-data-table__wrapper"], selectable=True)),
                        ft.DataCell(ft.Text(book.get("v-data-table__wrapper (2)"), selectable=True)),
                        ft.DataCell(ft.Text(book.get("v-data-table__wrapper (4)"), selectable=True)),
                    ]
                )
            )

        self.content = ft.Column(controls=[
            ft.Divider(color=ft.Colors.TRANSPARENT),
            ft.ResponsiveRow([
                ft.Column(col=7, controls=[ft.Text("管理カテゴリー", theme_style=ft.TextThemeStyle.TITLE_LARGE)]),
                ft.CupertinoSlidingSegmentedButton(
                    col=5,
                    selected_index=1,
                    controls=[
                        ft.Text("無印"),
                        ft.Text("ISBN"),
                        ft.Text("ＢＫ"),
                        ft.Text("ＤＶ"),
                        ft.Text("ＨＶ"),
                    ],
                )
            ]),
            ft.Column(controls=[shelf_table], scroll=ft.ScrollMode.AUTO, expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
        ])

