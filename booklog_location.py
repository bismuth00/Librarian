from returns.pipeline import is_successful
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import flet as ft
import re
import time
import util

class BooklogLocation(ft.Column):

    def __init__(self, page, driver, categories):
        super().__init__()
        self.page = page
        self.driver = driver
        self.categories = categories

    def build(self):
        self.table = ft.DataTable(
                columns = [
                    ft.DataColumn(ft.Text("")),
                    ft.DataColumn(ft.Text("ASIN")),
                    ft.DataColumn(ft.Text("書名")),
                    ft.DataColumn(ft.Text("変更前")),
                    ft.DataColumn(ft.Text("変更後")),
                ],
            )

        def clear():
            self.table.rows.clear()
            self.text.focus()
            self.page.update()

        def submit():
            with util.OpenWaitDialog(self.page, "書籍情報変更中…"):
                category_key = self.dropdown.value
                category_val = next((o.text for o in self.dropdown.options if o.key == category_key))
                category_val = re.sub(r" \([0-9]+\)", "", category_val)
                print("category_key:", category_key, "category_val:", category_val)
                pending = []
                def process(item):
                    try:
                        book = self.get_book_info(item)
                        select = Select(self.driver.find_element(By.NAME, 'category_id'))
                        select.select_by_value(category_key)
                        button = self.driver.find_element(By.CLASS_NAME, "positive")
                        time.sleep(0.2)
                        button.click()
                        time.sleep(0.2)
                        return book
                    except:
                        return None
                for result in util.process_text(process, self.text.value):
                    if is_successful(result):
                        book = result.unwrap()
                        next((c for c in self.categories if c['text'] == category_val))["count"] += 1
                        next((c for c in self.categories if c['text'] == book["category"]))["count"] -= 1
                        self.table.rows.insert(0,
                            ft.DataRow(
                                cells = [
                                    ft.DataCell(ft.Text(len(self.table.rows) + 1, selectable=True)),
                                    ft.DataCell(ft.Text(book["asin"], selectable=True)),
                                    ft.DataCell(ft.Text(book["title"], selectable=True)),
                                    ft.DataCell(ft.Text(book["category"], selectable=True)),
                                    ft.DataCell(ft.Text(category_val, selectable=True)),
                                ]
                            )
                        )
                    else:
                        pending.append(result.failure())
            util.update_dropdown_categories(self.dropdown, self.categories, self.page)
            if len(pending) == 1 and not re.match(r"^[0-9X]+$", pending[0].split("\t")[0]):
                pending.clear()
            self.text.value = "\n".join(pending)
            self.text.focus()
            self.page.update()
            if len(pending) > 0:
                util.OpenErrorDialog(self.page, "{}件の変更に失敗しました".format(len(pending)))

        self.text = ft.TextField(label="ISBN or ASIN", multiline=True, min_lines=5, max_lines=5)
        self.dropdown = util.create_dropdown_categories(self.categories)
        self.controls.extend([
                    ft.Divider(color=ft.Colors.TRANSPARENT),
                    self.text,
                    ft.ResponsiveRow([
                        ft.Column(col=10, controls=[self.dropdown]),
                        ft.FilledButton("まとめて変更", col=2, icon=ft.Icons.CHANGE_CIRCLE, on_click=lambda _: submit())
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Divider(),
                    ft.ResponsiveRow([
                        ft.Text("変更履歴", col=11, theme_style=ft.TextThemeStyle.TITLE_LARGE),
                        ft.FilledButton("クリア", col=1, icon=ft.Icons.CLEAR, on_click=lambda _: clear())
                    ]),
                    ft.Column(controls=[self.table], scroll=ft.ScrollMode.AUTO, expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
        ])
