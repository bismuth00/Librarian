from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import flet as ft
import re
import time
import util

class BooklogInventory(ft.Column):

    def __init__(self, page, driver, categories, config):
        super().__init__()
        self.page = page
        self.driver = driver
        self.categories = categories
        self.config = config

    def build(self):
        self.table = ft.DataTable(
                        columns = [
                            ft.DataColumn(ft.Text("")),
                            ft.DataColumn(ft.Text("ASIN")),
                            ft.DataColumn(ft.Text("書名")),
                            ft.DataColumn(ft.Text("タグ")),
                            ft.DataColumn(ft.Text("状態")),
                        ],
                    )

        def download():
            with util.OpenWaitDialog(self.page, "カテゴリ情報取得中…"):
                self.driver.get("https://booklog.jp/users/{}?category_id={}&display=card".format(self.config["username"], self.dropdown.value))
                actions = ActionChains(self.driver)
                items = self.driver.find_elements(By.CLASS_NAME, "shelf-item")
                while True and len(items) > 0:
                    actions.move_to_element(items[-1])
                    actions.perform()
                    time.sleep(1.5)
                    item_new = self.driver.find_elements(By.CLASS_NAME, "shelf-item")
                    if len(items) == len(item_new):
                        break
                    items = item_new
                self.table.rows.clear()

                options = []
                for key, value in util.STATE_DICT.items():
                    options.append(
                        ft.DropdownOption(
                            key=key,
                            text=value,
                        )
                    )

                for i in items:
                    title = i.find_element(By.XPATH, ".//*[@class='item-area-info-title']/a").text
                    asin = i.find_element(By.XPATH, ".//*[@class='item-area-image']/a").get_attribute('href').split("/")[-1]
                    tags = i.find_elements(By.XPATH, ".//*[@class='more-info-tags']")
                    if len(tags) > 0:
                        tags = tags[0].find_element(By.XPATH, "./ul/li/a").text
                    else:
                        tags = None
                    dd = ft.Dropdown(
                            border_width=0,
                            options=options,
                            value="unknown",
                        )
                    self.table.rows.append(
                        ft.DataRow(
                            cells = [
                                ft.DataCell(ft.Text(len(self.table.rows) + 1, selectable=True)),
                                ft.DataCell(ft.Text(asin, selectable=True)),
                                ft.DataCell(ft.Text(title, selectable=True)),
                                ft.DataCell(ft.Text(tags, selectable=True)),
                                ft.DataCell(dd),
                            ]
                        )
                    )
                self.text.focus()
                self.page.update()

        def submit():
            asin = self.text.value.strip()
            if re.match(r'^[0-9X]{12}[0-9X]$', asin):
                asin = util.isbn_to_asin(asin)
            for row in self.table.rows:
                if row.cells[1].content.value == asin:
                    row.cells[4].content.value = util.STATE_CHECKED_KEY
                    break
            self.text.value = ""
            self.text.focus()
            self.page.update()

        def inventory():
            with util.OpenWaitDialog(self.page, "書籍情報変更中…"):
                for row in self.table.rows:
                    if row.cells[4].content.value == util.STATE_UNKNOWN_KEY:
                        if row.cells[3].content.value == util.STATE_UNKNOWN_VALUE:
                            continue
                        _ = self.get_book_info(row.cells[1].content.value)
                        tags = self.driver.find_element(By.ID, 'tags')
                        tags.send_keys(" " + util.STATE_UNKNOWN_VALUE)
                    elif row.cells[4].content.value == util.STATE_CHECKED_KEY:
                        if row.cells[3].content.value != util.STATE_UNKNOWN_VALUE:
                            continue
                        _ = self.get_book_info(row.cells[1].content.value)
                        tags = self.driver.find_element(By.ID, 'tags')
                        tags.clear()
                    else:
                        continue
                    button = self.driver.find_element(By.CLASS_NAME, "positive")
                    time.sleep(0.2)
                    button.click()
                self.table.rows.clear()
                self.page.update()

        self.text = ft.TextField(label="ISBN or ASIN", on_submit=lambda _: submit(), min_lines=1, max_lines=5)
        self.dropdown = util.create_dropdown_categories(self.categories)
        self.controls.extend([
                    ft.Divider(color=ft.Colors.TRANSPARENT),
                    ft.ResponsiveRow([
                        ft.Column(col=8, controls=[self.dropdown]),
                        ft.FilledButton("データ取得", col=2, icon=ft.Icons.DOWNLOAD, on_click=lambda _: download()),
                        ft.FilledButton("棚卸終了", col=2, icon=ft.Icons.PIN_END, on_click=lambda _: inventory())
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    self.text,
                    ft.Divider(),
                    ft.Column(controls=[self.table], scroll=ft.ScrollMode.AUTO, expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
        ])
