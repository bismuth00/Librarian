import flet as ft

class CosmosInventory(ft.Column):
    def __init__(self, page, books):
        super().__init__()
        self.page = page
        self.books = books

    def build(self):

        self.text = ft.TextField(
            label="管理番号 or ISBN", min_lines=1, max_lines=5
        )

        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("")),
                ft.DataColumn(ft.Text("管理番号")),
                ft.DataColumn(ft.Text("書名")),
                ft.DataColumn(ft.Text("状態")),
            ],
        )

        self.controls.extend([
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
            self.text,
            ft.Divider(),
            ft.Column(
                controls=[self.table],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
        ])
