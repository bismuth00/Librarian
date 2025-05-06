# -*- coding: utf-8 -*-

import re
import subprocess
import time
from returns.pipeline import is_successful

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from pprint import pp
import flet as ft

import camera
import util

STATE_UNKNOWN_KEY = "unknown"
STATE_UNKNOWN_VALUE = "所在不明"
STATE_CHECKED_KEY = "checked"
STATE_CHECKED_VALUE = "確認済み"
STATE_DICT = {STATE_UNKNOWN_KEY:STATE_UNKNOWN_VALUE, STATE_CHECKED_KEY:STATE_CHECKED_VALUE, "add":"新規追加"}

def main(page: ft.Page):
    categories = []

    page.title = "蔵書管理"

    dialog_wait = ft.AlertDialog(
        modal=True,
        title=ft.Text(""))

    dialog_error = ft.AlertDialog(
        modal=True,
        title=ft.Text("登録エラー"),
        content=ft.Text(""),
        actions=[ft.TextButton("閉じる", on_click=lambda e: page.close(dialog_error))]
    )

    page.add(dialog_wait)
    page.add(dialog_error)
    dialog_wait.title.value = "初期化中…"
    page.open(dialog_wait)
    driver = util.login_booklog()

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
        shelf_text.focus()
        page.update()

    def history_clear(e):
        category_table.rows.clear()
        category_text.focus()
        page.update()

    def table_copy(e):
        text = "\t".join(map(lambda x: x.label.value, shelf_table.columns[1:]))
        for r in shelf_table.rows:
            text += "\n" + "\t".join(map(lambda x: x.content.value, r.cells[1:]))
        subprocess.run("clip", input=text, text=True)
        shelf_text.focus()

    def shelf_submit(control):
        def process(asin):
            if not re.match(r"^[0-9X]+$", asin):
                return None
            if not util.verify_asin(asin):
                return { "asin": asin, "title": "不正な入力", "author": "", "category": "" }
            try:
                return util.get_book_info(driver, asin)
            except:
                return { "asin": asin, "title": "エラー", "author": "", "category": "" }
        dialog_wait.title.value = "書籍情報取得中…"
        page.open(dialog_wait)
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
        page.update()
        page.close(dialog_wait)

    def inventory_submit(e):
        asin = e.control.value.strip()
        if re.match(r'^[0-9X]{12}[0-9X]$', asin):
            asin = util.isbn_to_asin(asin)
        for row in inventory_table.rows:
            if row.cells[1].content.value == asin:
                row.cells[4].content.value = STATE_CHECKED_KEY
                break
        e.control.value = ""
        e.control.focus()
        page.update()

    def inventory_end(e):
        dialog_wait.title.value = "書籍情報変更中…"
        page.open(dialog_wait)
        for row in inventory_table.rows:
            if row.cells[4].content.value == STATE_UNKNOWN_KEY:
                if row.cells[3].content.value == STATE_UNKNOWN_VALUE:
                    continue
                _ = util.get_book_info(driver, row.cells[1].content.value)
                tags = driver.find_element(By.ID, 'tags')
                tags.send_keys(" " + STATE_UNKNOWN_VALUE)
            elif row.cells[4].content.value == STATE_CHECKED_KEY:
                if row.cells[3].content.value != STATE_UNKNOWN_VALUE:
                    continue
                _ = util.get_book_info(driver, row.cells[1].content.value)
                tags = driver.find_element(By.ID, 'tags')
                tags.clear()
            else:
                continue
            button = driver.find_element(By.CLASS_NAME, "positive")
            time.sleep(0.2)
            button.click()
        inventory_table.rows.clear()
        page.update()
        page.close(dialog_wait)

    def bulk_submit(e):
        dialog_wait.title.value = "書籍情報変更中…"
        page.open(dialog_wait)
        category_key = drop_simple.value
        category_val = next((o.text for o in drop_simple.options if o.key == category_key))
        category_val = re.sub(r" \([0-9]+\)", "", category_val)
        pending = []
        def process(item):
            try:
                book = util.get_book_info(driver, item)
                select = Select(driver.find_element(By.NAME, 'category_id'))
                select.select_by_value(category_key)
                button = driver.find_element(By.CLASS_NAME, "positive")
                time.sleep(0.2)
                button.click()
                return book
            except:
                return None
        for result in util.process_text(process, category_text.value):
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
        category_text.value = "\n".join(pending)
        category_text.focus()
        page.update()
        page.close(dialog_wait)
        if len(pending) > 0:
            dialog_error.content.value = "{}件の変更に失敗しました".format(len(pending))
            page.open(dialog_error)

    def shelf_download(e):
        dialog_wait.title.value = "カテゴリ情報取得中…"
        page.open(dialog_wait)
        driver.get("https://booklog.jp/users/{}?category_id={}&display=card".format(util.config["username"], drop_detail.value))
        actions = ActionChains(driver)
        items = driver.find_elements(By.CLASS_NAME, "shelf-item")
        while True and len(items) > 0:
            actions.move_to_element(items[-1])
            actions.perform()
            time.sleep(1.5)
            item_new = driver.find_elements(By.CLASS_NAME, "shelf-item")
            if len(items) == len(item_new):
                break
            items = item_new
        inventory_table.rows.clear()

        options = []
        for key, value in STATE_DICT.items():
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
        inventory_text.focus()
        page.update()
        page.close(dialog_wait)

    shelf_text = ft.TextField(label="ISBN or ASIN", on_submit=lambda e: shelf_submit(e.control), min_lines=1, max_lines=5)
    category_text = ft.TextField(label="ISBN or ASIN", multiline=True, min_lines=5, max_lines=5)
    inventory_text = ft.TextField(label="ISBN or ASIN", on_submit=inventory_submit, min_lines=1, max_lines=5)

    drop_simple = ft.Dropdown(label="カテゴリ", value="0")
    drop_detail = ft.Dropdown(label="カテゴリ", value="0")
    categories = util.update_category(driver)
    util.update_dropdown(categories, drop_simple, drop_detail)

    def get_camera_isbn(e):
        shelf_text.value += e
        shelf_submit(shelf_text)
    
    tab = ft.Tabs(
        animation_duration=200,
        expand=True,
        tabs=[
            ft.Tab(
                text="書籍情報",
                icon=ft.Icons.MENU_BOOK,
                content=ft.Column(controls=[
                        ft.Divider(color=ft.Colors.TRANSPARENT),
                        shelf_text,
                        ft.Divider(),
                        ft.ResponsiveRow([
                            ft.Column(col=9, controls=[ft.Text("検索履歴", theme_style=ft.TextThemeStyle.TITLE_LARGE)]),
                            ft.Column(col=1, controls=[ft.FilledButton("カメラ", icon=ft.Icons.COPY, on_click=lambda e: camera.test_pyocr(get_camera_isbn))]),
                            ft.Column(col=1, controls=[ft.FilledButton("コピー", icon=ft.Icons.COPY, on_click=table_copy)]),
                            ft.Column(col=1, controls=[ft.FilledButton("クリア", icon=ft.Icons.CLEAR, on_click=table_clear)])
                        ]),
                        ft.Column(controls=[shelf_table], scroll=ft.ScrollMode.AUTO, expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
                    ]),
            ),
            ft.Tab(
                text="カテゴリ変更",
                icon=ft.Icons.LIBRARY_BOOKS,
                content=ft.Column(controls=[
                        ft.Divider(color=ft.Colors.TRANSPARENT),
                        category_text,
                        ft.ResponsiveRow([
                            ft.Column(col=10, controls=[drop_simple]),
                            ft.Column(col=2, horizontal_alignment=ft.CrossAxisAlignment.STRETCH, controls=[ft.FilledButton("まとめて変更", icon=ft.Icons.CHANGE_CIRCLE, on_click=bulk_submit)]),
                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Divider(),
                        ft.ResponsiveRow([
                            ft.Column(col=11, controls=[ft.Text("変更履歴", theme_style=ft.TextThemeStyle.TITLE_LARGE)]),
                            ft.Column(col=1, controls=[ft.FilledButton("クリア", icon=ft.Icons.CLEAR, on_click=history_clear)])
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
                            ft.Column(col=2, horizontal_alignment=ft.CrossAxisAlignment.STRETCH, controls=[ft.FilledButton("データ取得", icon=ft.Icons.DOWNLOAD, on_click=shelf_download)]),
                            ft.Column(col=2, horizontal_alignment=ft.CrossAxisAlignment.STRETCH, controls=[ft.FilledButton("棚卸終了", icon=ft.Icons.PIN_END, on_click=inventory_end)]),
                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        inventory_text,
                        ft.Divider(),
                        ft.Column(controls=[inventory_table], scroll=ft.ScrollMode.AUTO, expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
                   ]),
            ),
        ],
    )
    
    page.add(tab)

    shelf_text.focus()
    category_text.focus()
    inventory_text.focus()

    page.window.always_on_top = True
    page.update()
    page.window.always_on_top = False

    page.close(dialog_wait)

ft.app(target=main)

# string = '''
# Id	Title	Category
# 483224986X	             NEW GAME! 8 (まんがタイムKRコミックス)           	ブックワゴンG-3
# 4832245465	             New Game! 2 (まんがタイムKRコミックス)           	ブックワゴンG-3
# 4832244140	             New Game! 1 (まんがタイムKRコミックス)           	ブックワゴンG-3
# 4832271539	             NEW GAME! 10 (まんがタイムKRコミックス)           	ブックワゴンG-3
# 4832271016	             NEW GAME! 9 (まんがタイムKRコミックス)           	ブックワゴンG-3
# 4832249290	             NEW GAME!(7) (まんがタイムKRコミックス)           	ブックワゴンG-3
# 4832248472	             NEW GAME!(6) (まんがタイムKRコミックス)           	ブックワゴンG-3
# 4832247212	             NEW GAME!(5) ―THE SPINOFF!― (まんがタイムKRコミックス)           	ブックワゴンG-3
# 4832247204	             NEW GAME!(4) (まんがタイムKRコミックス)           	ブックワゴンG-3
# 4832246569	             NEW GAME! 3 (まんがタイムKRコミックス)           	ブックワゴンG-3
# '''

# string = '''
# 9784832249868
# 9784832245464
# 9784832244146
# '''
