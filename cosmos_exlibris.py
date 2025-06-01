import flet as ft


class CosmosExlibris(ft.Column):
    def __init__(self, page, books):
        super().__init__()
        self.page = page
        self.books = books

    def build(self):
        self.list = ft.Column()

        def appendBookTable(book):
            self.table.rows.insert(
                0,
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Text(len(self.table.rows) + 1, selectable=True)
                        ),
                        ft.DataCell(ft.Text(book["class_id"], selectable=True)),
                        ft.DataCell(ft.Text(book["category"], selectable=True)),
                        ft.DataCell(ft.Text(book["title"], selectable=True)),
                        ft.DataCell(ft.Text(book.get("location", "不明"), selectable=True)),
                    ]
                ),
            )
            self.list.clean()
            self.text.value = ""
            self.text.focus()
            self.page.update()

        def submit(e):
            if len(self.list.controls) != 1:
                e.control.focus()
                return
            appendBookTable(self.list.controls[0].book)

        def change(e):
            candidate = []
            for book in self.books.values():
                ids = book["class_id"].split("-")
                if len(ids) > 1 and not ids[0].isdecimal():
                    id = ids[1]
                else:
                    id = ids[0]
                if id == e.data:
                    candidate.append(book)
            self.list.controls.clear()
            if len(candidate) > 0:
                for c in candidate:
                    tile = ft.CupertinoListTile(
                            additional_info=ft.Text(c["class_id"]),
                            leading=ft.Icon(name=ft.CupertinoIcons.BOOK),
                            title=ft.Text(c["title"]),
                            on_click=lambda _: appendBookTable(c)
                        )
                    tile.book = c
                    self.list.controls.append(tile)
            self.page.update()

        self.text = ft.TextField(label="管理番号 or ISBN", on_change=change, on_submit=submit)

        self.table = ft.DataTable(
            sort_column_index=1,
            columns=[
                ft.DataColumn(ft.Text("")),
                ft.DataColumn(ft.Text("管理番号")),
                ft.DataColumn(ft.Text("カテゴリ")),
                ft.DataColumn(ft.Text("書名")),
                ft.DataColumn(ft.Text("場所")),
            ],
        )

        self.controls.extend(
            [
                ft.Divider(color=ft.Colors.TRANSPARENT),
                ft.ResponsiveRow(
                    [
                        ft.Column(col=4, controls=[self.text]),
                        ft.Column(col=8, controls=[self.list]),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Column(
                    controls=[self.table],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                ),
            ]
        )
