import subprocess
from returns.pipeline import is_successful
import flet as ft
import re
import camera
import util


class BooklogShelf(ft.Column):
    def __init__(self, page, driver):
        super().__init__()
        self.page = page
        self.driver = driver

    def build(self):
        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("")),
                ft.DataColumn(ft.Text("ASIN")),
                ft.DataColumn(ft.Text("書名")),
                ft.DataColumn(ft.Text("作者")),
                ft.DataColumn(ft.Text("カテゴリ")),
            ],
        )

        def submit(control):
            def process(asin):
                if not re.match(r"^[0-9X]+$", asin):
                    return None
                if not util.verify_asin(asin):
                    return {
                        "asin": asin,
                        "title": "不正な入力",
                        "author": "",
                        "category": "",
                    }
                try:
                    return util.get_book_info(self.driver, asin)
                except:
                    return {
                        "asin": asin,
                        "title": "エラー",
                        "author": "",
                        "category": "",
                    }

            with util.OpenWaitDialog(self.page, "書籍情報取得中…"):
                for result in util.process_text(process, control.value):
                    if not is_successful(result):
                        continue
                    book = result.unwrap()
                    self.table.rows.insert(
                        0,
                        ft.DataRow(
                            cells=[
                                ft.DataCell(
                                    ft.Text(len(self.table.rows) + 1, selectable=True)
                                ),
                                ft.DataCell(ft.Text(book["asin"], selectable=True)),
                                ft.DataCell(ft.Text(book["title"], selectable=True)),
                                ft.DataCell(ft.Text(book["author"], selectable=True)),
                                ft.DataCell(ft.Text(book["category"], selectable=True)),
                            ]
                        ),
                    )
                control.value = ""
                control.focus()
                self.page.update()

        def proc_camera(isbn):
            self.text.value += isbn
            submit(self.text)

        def clear():
            self.table.rows.clear()
            self.text.focus()
            self.page.update()

        def copy():
            text = "\t".join(map(lambda x: x.label.value, self.table.columns[1:]))
            for r in self.table.rows:
                text += "\n" + "\t".join(map(lambda x: x.content.value, r.cells[1:]))
            subprocess.run("clip", input=text, text=True)
            self.text.focus()

        self.text = ft.TextField(
            label="ISBN or ASIN",
            on_submit=lambda e: submit(e.control),
            min_lines=1,
            max_lines=5,
        )
        self.controls.extend(
            [
                ft.Divider(color=ft.Colors.TRANSPARENT),
                self.text,
                ft.Divider(),
                ft.ResponsiveRow(
                    [
                        ft.Text(
                            "検索履歴", col=9, theme_style=ft.TextThemeStyle.TITLE_LARGE
                        ),
                        ft.FilledButton(
                            "カメラ",
                            col=1,
                            icon=ft.Icons.COPY,
                            on_click=lambda _: camera.test_pyocr(proc_camera),
                        ),
                        ft.FilledButton(
                            "コピー",
                            col=1,
                            icon=ft.Icons.COPY,
                            on_click=lambda _: copy(),
                        ),
                        ft.FilledButton(
                            "クリア",
                            col=1,
                            icon=ft.Icons.CLEAR,
                            on_click=lambda _: clear(),
                        ),
                    ]
                ),
                ft.Column(
                    controls=[self.table],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                ),
            ]
        )
