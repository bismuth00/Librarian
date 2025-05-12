import subprocess
import time
import re
from returns.pipeline import is_successful
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import flet as ft
import camera
import util

class BookLog(ft.Container):
    def __init__(self, page, dialog_wait, dialog_error, config):
        super().__init__()
        self.page = page
        self.dialog_wait = dialog_wait
        self.dialog_error = dialog_error
        self.config = config

    def build(self):
        self.driver = self.login()

        shelf_table = ft.DataTable(
                    columns = [
                        ft.DataColumn(ft.Text("")),
                        ft.DataColumn(ft.Text("ASIN")),
                        ft.DataColumn(ft.Text("書名")),
                        ft.DataColumn(ft.Text("作者")),
                        ft.DataColumn(ft.Text("カテゴリ")),
                    ],
                )

        category_table = ft.DataTable(
                    columns = [
                        ft.DataColumn(ft.Text("")),
                        ft.DataColumn(ft.Text("ASIN")),
                        ft.DataColumn(ft.Text("書名")),
                        ft.DataColumn(ft.Text("変更前")),
                        ft.DataColumn(ft.Text("変更後")),
                    ],
                )

        inventory_table = ft.DataTable(
                    columns = [
                        ft.DataColumn(ft.Text("")),
                        ft.DataColumn(ft.Text("ASIN")),
                        ft.DataColumn(ft.Text("書名")),
                        ft.DataColumn(ft.Text("タグ")),
                        ft.DataColumn(ft.Text("状態")),
                    ],
                )

        def table_clear(e):
            shelf_table.rows.clear()
            self.shelf_text.focus()
            self.page.update()

        def history_clear(e):
            category_table.rows.clear()
            self.category_text.focus()
            self.page.update()

        def table_copy(e):
            text = "\t".join(map(lambda x: x.label.value, shelf_table.columns[1:]))
            for r in shelf_table.rows:
                text += "\n" + "\t".join(map(lambda x: x.content.value, r.cells[1:]))
            subprocess.run("clip", input=text, text=True)
            self.shelf_text.focus()

        def shelf_submit(control):
            def process(asin):
                if not re.match(r"^[0-9X]+$", asin):
                    return None
                if not util.verify_asin(asin):
                    return { "asin": asin, "title": "不正な入力", "author": "", "category": "" }
                try:
                    return self.get_book_info(asin)
                except:
                    return { "asin": asin, "title": "エラー", "author": "", "category": "" }
            with util.OpenDialog(self.page, self.dialog_wait, "書籍情報取得中…"):
                for result in util.process_text(process, control.value):
                    if not is_successful(result): continue
                    book = result.unwrap()
                    shelf_table.rows.insert(0,
                        ft.DataRow(
                            cells = [
                                ft.DataCell(ft.Text(len(shelf_table.rows) + 1, selectable=True)),
                                ft.DataCell(ft.Text(book["asin"], selectable=True)),
                                ft.DataCell(ft.Text(book["title"], selectable=True)),
                                ft.DataCell(ft.Text(book["author"], selectable=True)),
                                ft.DataCell(ft.Text(book["category"], selectable=True)),
                            ]
                        )
                    )
                control.value = ""
                control.focus()
                self.page.update()

        def inventory_submit(e):
            asin = e.control.value.strip()
            if re.match(r'^[0-9X]{12}[0-9X]$', asin):
                asin = util.isbn_to_asin(asin)
            for row in inventory_table.rows:
                if row.cells[1].content.value == asin:
                    row.cells[4].content.value = util.STATE_CHECKED_KEY
                    break
            e.control.value = ""
            e.control.focus()
            self.page.update()

        def inventory_end(e):
            with util.OpenDialog(self.page, self.dialog_wait, "書籍情報変更中…"):
                for row in inventory_table.rows:
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
                inventory_table.rows.clear()
                self.page.update()

        def bulk_submit(e):
            with util.OpenDialog(self.page, self.dialog_wait, "書籍情報変更中…"):
                category_key = drop_simple.value
                category_val = next((o.text for o in drop_simple.options if o.key == category_key))
                category_val = re.sub(r" \([0-9]+\)", "", category_val)
                pending = []
                def process(item):
                    try:
                        book = util.get_book_info(self.driver, item)
                        select = Select(self.driver.find_element(By.NAME, 'category_id'))
                        select.select_by_value(category_key)
                        button = self.driver.find_element(By.CLASS_NAME, "positive")
                        time.sleep(0.2)
                        button.click()
                        return book
                    except:
                        return None
                for result in util.process_text(process, self.category_text.value):
                    if is_successful(result):
                        book = result.unwrap()
                        next((c for c in categories if c['text'] == category_val))["count"] += 1
                        next((c for c in categories if c['text'] == book["category"]))["count"] -= 1
                        category_table.rows.insert(0,
                            ft.DataRow(
                                cells = [
                                    ft.DataCell(ft.Text(len(category_table.rows) + 1, selectable=True)),
                                    ft.DataCell(ft.Text(book["asin"], selectable=True)),
                                    ft.DataCell(ft.Text(book["title"], selectable=True)),
                                    ft.DataCell(ft.Text(book["category"], selectable=True)),
                                    ft.DataCell(ft.Text(category_val, selectable=True)),
                                ]
                            )
                        )
                    else:
                        pending.append(result.failure())
                util.update_dropdown(categories, drop_simple, drop_detail)
                if len(pending) == 1 and not re.match(r"^[0-9X]+$", pending[0].split("\t")[0]):
                    pending.clear()
                self.category_text.value = "\n".join(pending)
                self.category_text.focus()
                self.page.update()
            if len(pending) > 0:
                self.dialog_error.content.value = "{}件の変更に失敗しました".format(len(pending))
                self.page.open(self.dialog_error)

        def shelf_download(e):
            with util.OpenDialog(self.page, self.dialog_wait, "カテゴリ情報取得中…"):
                self.driver.get("https://booklog.jp/users/{}?category_id={}&display=card".format(self.config["username"], drop_detail.value))
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
                inventory_table.rows.clear()

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
                    inventory_table.rows.append(
                        ft.DataRow(
                            cells = [
                                ft.DataCell(ft.Text(len(inventory_table.rows) + 1, selectable=True)),
                                ft.DataCell(ft.Text(asin, selectable=True)),
                                ft.DataCell(ft.Text(title, selectable=True)),
                                ft.DataCell(ft.Text(tags, selectable=True)),
                                ft.DataCell(dd),
                            ]
                        )
                    )
                self.inventory_text.focus()
                self.page.update()

        self.shelf_text = ft.TextField(label="ISBN or ASIN", on_submit=lambda e: shelf_submit(e.control), min_lines=1, max_lines=5)
        self.category_text = ft.TextField(label="ISBN or ASIN", multiline=True, min_lines=5, max_lines=5)
        self.inventory_text = ft.TextField(label="ISBN or ASIN", on_submit=inventory_submit, min_lines=1, max_lines=5)

        drop_simple = ft.Dropdown(label="カテゴリ", value="0")
        drop_detail = ft.Dropdown(label="カテゴリ", value="0")
        categories = self.update_category()
        util.update_dropdown(categories, drop_simple, drop_detail)

        def get_camera_isbn(e):
            self.shelf_text.value += e
            shelf_submit(self.shelf_text)
        
        tab = ft.Tabs(
            animation_duration=200,
            expand=True,
            is_secondary=True,
            tabs=[
                ft.Tab(
                    text="書籍情報",
                    icon=ft.Icons.MENU_BOOK,
                    content=ft.Column(controls=[
                            ft.Divider(color=ft.Colors.TRANSPARENT),
                            self.shelf_text,
                            ft.Divider(),
                            ft.ResponsiveRow([
                                ft.Text("検索履歴", col=9, theme_style=ft.TextThemeStyle.TITLE_LARGE),
                                ft.FilledButton("カメラ", col=1, icon=ft.Icons.COPY, on_click=lambda e: camera.test_pyocr(get_camera_isbn)),
                                ft.FilledButton("コピー", col=1, icon=ft.Icons.COPY, on_click=table_copy),
                                ft.FilledButton("クリア", col=1, icon=ft.Icons.CLEAR, on_click=table_clear)
                            ]),
                            ft.Column(controls=[shelf_table], scroll=ft.ScrollMode.AUTO, expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
                        ]),
                ),
                ft.Tab(
                    text="カテゴリ変更",
                    icon=ft.Icons.LIBRARY_BOOKS,
                    content=ft.Column(controls=[
                            ft.Divider(color=ft.Colors.TRANSPARENT),
                            self.category_text,
                            ft.ResponsiveRow([
                                ft.Column(col=10, controls=[drop_simple]),
                                ft.FilledButton("まとめて変更", col=2, icon=ft.Icons.CHANGE_CIRCLE, on_click=bulk_submit)
                            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            ft.Divider(),
                            ft.ResponsiveRow([
                                ft.Text("変更履歴", col=11, theme_style=ft.TextThemeStyle.TITLE_LARGE),
                                ft.FilledButton("クリア", col=1, icon=ft.Icons.CLEAR, on_click=history_clear)
                            ]),
                            ft.Column(controls=[category_table], scroll=ft.ScrollMode.AUTO, expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
                        ]),
                ),
                ft.Tab(
                    text="棚卸",
                    icon=ft.Icons.MOVE_DOWN,
                    content=ft.Column(controls=[
                            ft.Divider(color=ft.Colors.TRANSPARENT),
                            ft.ResponsiveRow([
                                ft.Column(col=8, controls=[drop_detail]),
                                ft.FilledButton("データ取得", col=2, icon=ft.Icons.DOWNLOAD, on_click=shelf_download),
                                ft.FilledButton("棚卸終了", col=2, icon=ft.Icons.PIN_END, on_click=inventory_end)
                            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            self.inventory_text,
                            ft.Divider(),
                            ft.Column(controls=[inventory_table], scroll=ft.ScrollMode.AUTO, expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
                    ]),
                ),
            ],
        )
        self.content = tab
    def did_mount(self):
        self.shelf_text.focus()
        self.category_text.focus()
        self.inventory_text.focus()

    def login(self):
        options = webdriver.ChromeOptions()
        options.set_capability('pageLoadStrategy', 'eager')
        # options.add_argument("--headless")
        # options.add_argument("--window-size=1200x1000")

        driver = webdriver.Chrome(options = options)
        driver.implicitly_wait(0)

        driver.get("https://booklog.jp/login")

        e = driver.find_element(By.ID, "account")
        e.clear()
        e.send_keys(self.config["username"])
        time.sleep(0.1)
        e = driver.find_element(By.ID, "password")
        e.clear()
        e.send_keys(self.config["password"])
        time.sleep(1)

        # フォームを送信
        button = driver.find_element(By.ID, "login_submit_button")
        driver.execute_script("arguments[0].click();", button)
        time.sleep(0.1)
        button.click() # <- これだけだと不正検知に引っ掛かるので上の行でイベントを発火させる

        while driver.current_url == "https://booklog.jp/login":
            time.sleep(1)

        return driver

    def update_category(self):
        self.driver.get("https://booklog.jp/users/{}".format(self.config["username"]))
        self.driver.find_element(By.CLASS_NAME, "shelf-header-menu-category-modal").click()
        links = self.driver.find_elements(By.XPATH, "//*[@id='categories']/*/a")
        categories = []
        for link in links:
            r = re.search(r'\?category_id=([0-9a-z]+)', link.get_attribute('href'))
            key = r.group(1)
            if key == 'none': key = "0"
            r = re.search(r' \(([0-9]+)\)', link.text)
            categories.append({"key": key, "text": link.text.replace(r.group(), ''), "count": int(r.group(1))})
        self.driver.find_element(By.CLASS_NAME, "modal-close").click()
        return categories

    def get_book_info(self, asin):
        self.driver.get("https://booklog.jp/edit/1/{}".format(asin))
        title = self.driver.find_element(By.CLASS_NAME, "titleLink").text
        author = self.driver.find_element(By.CLASS_NAME, "item-info-author").text
        try:
            category = Select(self.driver.find_element(By.NAME, "category_id")).all_selected_options[0].text
            tags = self.driver.find_element(By.ID, "tags").text
        except:
            category = "未登録"
            tags = ""
        return { "asin": asin, "title": title, "author": author, "category": category, "tags": tags }
