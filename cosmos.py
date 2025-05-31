import json
import flet as ft


class Cosmos(ft.Container):
    def __init__(self, page):
        super().__init__()
        self.books = json.load(open("books.json", "r", encoding="utf-8"))
        self.page = page

    def build(self):
        self.list_tiles = ft.Column()

        def shelf_change(e):
            candidate = []
            for book in self.books.values():
                ids = book["class_id"].split("-")
                if len(ids) > 1 and not ids[0].isdecimal():
                    id = ids[1]
                else:
                    id = ids[0]
                if id == e.data:
                    candidate.append(book)
            self.list_tiles.controls.clear()
            if len(candidate) > 0:
                for c in candidate:
                    self.list_tiles.controls.append(
                        ft.CupertinoListTile(
                            additional_info=ft.Text(c["class_id"]),
                            leading=ft.Icon(name=ft.CupertinoIcons.BOOK),
                            title=ft.Text(c["title"])
                        )                    
                    )
            self.page.update()

        self.shelf_text = ft.TextField(label="管理番号 or ISBN", on_change=shelf_change)
        self.inventory_text = ft.TextField(
            label="管理番号 or ISBN", min_lines=1, max_lines=5
        )

        self.shelf_table = ft.DataTable(
            sort_column_index=1,
            columns=[
                ft.DataColumn(ft.Text("")),
                ft.DataColumn(ft.Text("管理番号")),
                ft.DataColumn(ft.Text("カテゴリ")),
                ft.DataColumn(ft.Text("書名")),
                ft.DataColumn(ft.Text("場所")),
            ],
        )

        self.inventory_table = ft.DataTable(
            columns=[
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
                    content=ft.Column(
                        controls=[
                            ft.Divider(color=ft.Colors.TRANSPARENT),
                            ft.ResponsiveRow(
                                [
                                    ft.Column(col=4, controls=[self.shelf_text]),
                                    ft.Column(col=8, controls=[self.list_tiles]),
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Column(
                                controls=[self.shelf_table],
                                scroll=ft.ScrollMode.AUTO,
                                expand=True,
                                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                            ),
                        ]
                    ),
                ),
                ft.Tab(
                    text="棚卸",
                    icon=ft.Icons.MOVE_DOWN,
                    content=ft.Column(
                        controls=[
                            ft.Divider(color=ft.Colors.TRANSPARENT),
                            ft.ResponsiveRow(
                                [
                                    ft.Column(col=8, controls=[]),
                                    ft.FilledButton(
                                        "データ取得", col=2, icon=ft.Icons.DOWNLOAD
                                    ),
                                    ft.FilledButton(
                                        "棚卸終了", col=2, icon=ft.Icons.PIN_END
                                    ),
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            self.inventory_text,
                            ft.Divider(),
                            ft.Column(
                                controls=[self.inventory_table],
                                scroll=ft.ScrollMode.AUTO,
                                expand=True,
                                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                            ),
                        ]
                    ),
                ),
            ],
        )
