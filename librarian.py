# -*- coding: utf-8 -*-

import re
import subprocess
import time
from returns.result import Failure, Success
from returns.pipeline import is_successful

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from pprint import pp
import flet as ft
import json

import camera

config = json.load(open("config.json", "r", encoding="utf-8"))

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
    driver = login_booklog()

    table = ft.DataTable(
                columns = [
                    ft.DataColumn(ft.Text("")),
                    ft.DataColumn(ft.Text("ASIN")),
                    ft.DataColumn(ft.Text("書名")),
                    ft.DataColumn(ft.Text("作者")),
                    ft.DataColumn(ft.Text("カテゴリ")),
                ],
            )

    history = ft.DataTable(
                columns = [
                    ft.DataColumn(ft.Text("")),
                    ft.DataColumn(ft.Text("ASIN")),
                    ft.DataColumn(ft.Text("書名")),
                    ft.DataColumn(ft.Text("変更前")),
                    ft.DataColumn(ft.Text("変更後")),
                ],
            )

    shelf = ft.DataTable(
                columns = [
                    ft.DataColumn(ft.Text("")),
                    ft.DataColumn(ft.Text("ASIN")),
                    ft.DataColumn(ft.Text("書名")),
                    ft.DataColumn(ft.Text("作者")),
                    ft.DataColumn(ft.Text("確認")),
                ],
            )

    def table_clear(e):
        table.rows.clear()
        isbn.focus()
        page.update()

    def history_clear(e):
        history.rows.clear()
        text.focus()
        page.update()

    def table_copy(e):
        text = "\t".join(map(lambda x: x.label.value, table.columns[1:]))
        for r in table.rows:
            text += "\n" + "\t".join(map(lambda x: x.content.value, r.cells[1:]))
        subprocess.run("clip", input=text, text=True)
        isbn.focus()

    def isbn_submit(e):
        def process(asin):
            if not re.match(r"^[0-9X]+$", asin):
                return None
            if not verify_asin(asin):
                return { "asin": asin, "title": "不正な入力", "author": "", "category": "" }
            try:
                return get_book_info(driver, asin)
            except:
                return { "asin": asin, "title": "エラー", "author": "", "category": "" }
        dialog_wait.title.value = "書籍情報取得中…"
        page.open(dialog_wait)
        for result in process_text(process, e.control.value):
            if not is_successful(result): continue
            book = result.unwrap()
            table.rows.insert(0,
                ft.DataRow(
                    cells = [
                        ft.DataCell(ft.Text(len(table.rows) + 1, selectable=True)),
                        ft.DataCell(ft.Text(book["asin"], selectable=True)),
                        ft.DataCell(ft.Text(book["title"], selectable=True)),
                        ft.DataCell(ft.Text(book["author"], selectable=True)),
                        ft.DataCell(ft.Text(book["category"], selectable=True)),
                    ]
                )
            )
        e.control.value = ""
        e.control.focus()
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
                book = get_book_info(driver, item)
                select = Select(driver.find_element(By.NAME, 'category_id'))
                select.select_by_value(category_key)
                button = driver.find_element(By.CLASS_NAME, "positive")
                time.sleep(0.1)
                button.click()
                return book
            except:
                return None
        for result in process_text(process, text.value):
            if is_successful(result):
                book = result.unwrap()
                next((c for c in categories if c['text'] == category_val))["count"] += 1
                next((c for c in categories if c['text'] == book["category"]))["count"] -= 1
                history.rows.insert(0,
                    ft.DataRow(
                        cells = [
                            ft.DataCell(ft.Text(len(history.rows) + 1, selectable=True)),
                            ft.DataCell(ft.Text(book["asin"], selectable=True)),
                            ft.DataCell(ft.Text(book["title"], selectable=True)),
                            ft.DataCell(ft.Text(book["category"], selectable=True)),
                            ft.DataCell(ft.Text(category_val, selectable=True)),
                        ]
                    )
                )
            else:
                pending.append(result.failure())
        update_dropdown(categories, drop_simple, drop_detail)
        if len(pending) == 1 and not re.match(r"^[0-9X]+$", pending[0].split("\t")[0]):
            pending.clear()
        text.value = "\n".join(pending)
        text.focus()
        page.update()
        page.close(dialog_wait)
        if len(pending) > 0:
            dialog_error.content.value = "{}件の変更に失敗しました".format(len(pending))
            page.open(dialog_error)

    def shelf_download(e):
        dialog_wait.title.value = "カテゴリ情報取得中…"
        page.open(dialog_wait)
        driver.get("https://booklog.jp/users/{}?category_id={}&display=card".format(config["username"], drop_detail.value))
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
        shelf.rows.clear()

        options = []
        for key, value in {"unknown":"未確認", "checked":"確認済み", "add":"追加"}.items():
            options.append(
                ft.DropdownOption(
                    key=value
                )
            )
                    
        for i in items:
            title = i.find_element(By.XPATH, ".//*[@class='item-area-info-title']/a").text
            author = i.find_element(By.XPATH, ".//*[@class='author-link']").text
            asin = i.find_element(By.XPATH, ".//*[@class='item-area-image']/a").get_attribute('href').split("/")[-1]
            dd = ft.Dropdown(
                    border_width=0,
                    options=options,
                    value="未確認",
                )
            shelf.rows.append(
                ft.DataRow(
                    cells = [
                        ft.DataCell(ft.Text(len(shelf.rows) + 1, selectable=True)),
                        ft.DataCell(ft.Text(asin, selectable=True)),
                        ft.DataCell(ft.Text(title, selectable=True)),
                        ft.DataCell(ft.Text(author, selectable=True)),
                        ft.DataCell(dd),
                    ]
                )
            )
        page.update()
        page.close(dialog_wait)

    isbn = ft.TextField(label="ISBN or ASIN", on_submit=isbn_submit, min_lines=1, max_lines=5)
    text = ft.TextField(label="ISBN or ASIN", multiline=True, min_lines=5, max_lines=5)

    drop_simple = ft.Dropdown(label="カテゴリ", value="0")
    drop_detail = ft.Dropdown(label="カテゴリ", value="0")
    categories = update_category(driver)
    update_dropdown(categories, drop_simple, drop_detail)

    tab = ft.Tabs(
        animation_duration=200,
        expand=True,
        tabs=[
            ft.Tab(
                text="書籍情報",
                icon=ft.Icons.MENU_BOOK,
                content=ft.Column(controls=[
                        ft.Divider(color=ft.Colors.TRANSPARENT),
                        isbn,
                        ft.Divider(),
                        ft.ResponsiveRow([
                            ft.Column(col=9, controls=[ft.Text("検索履歴", theme_style=ft.TextThemeStyle.TITLE_LARGE)]),
                            ft.Column(col=1, controls=[ft.FilledButton("カメラ", icon=ft.Icons.COPY, on_click=camera.test_pyocr)]),
                            ft.Column(col=1, controls=[ft.FilledButton("コピー", icon=ft.Icons.COPY, on_click=table_copy)]),
                            ft.Column(col=1, controls=[ft.FilledButton("クリア", icon=ft.Icons.CLEAR, on_click=table_clear)])
                        ]),
                        ft.Column(controls=[table], scroll=ft.ScrollMode.AUTO, expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
                    ]),
            ),
            ft.Tab(
                text="カテゴリ変更",
                icon=ft.Icons.LIBRARY_BOOKS,
                content=ft.Column(controls=[
                        ft.Divider(color=ft.Colors.TRANSPARENT),
                        text,
                        ft.ResponsiveRow([
                            ft.Column(col=10, controls=[drop_simple]),
                            ft.Column(col=2, horizontal_alignment=ft.CrossAxisAlignment.STRETCH, controls=[ft.FilledButton("まとめて変更", icon=ft.Icons.CHANGE_CIRCLE, on_click=bulk_submit)]),
                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Divider(),
                        ft.ResponsiveRow([
                            ft.Column(col=11, controls=[ft.Text("変更履歴", theme_style=ft.TextThemeStyle.TITLE_LARGE)]),
                            ft.Column(col=1, controls=[ft.FilledButton("クリア", icon=ft.Icons.CLEAR, on_click=history_clear)])
                        ]),
                        ft.Column(controls=[history], scroll=ft.ScrollMode.AUTO, expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
                    ]),
            ),
            ft.Tab(
                text="棚卸",
                icon=ft.Icons.MOVE_DOWN,
                content=ft.Column(controls=[
                        ft.Divider(color=ft.Colors.TRANSPARENT),
                        ft.ResponsiveRow([
                            ft.Column(col=10, controls=[drop_detail]),
                            ft.Column(col=2, horizontal_alignment=ft.CrossAxisAlignment.STRETCH, controls=[ft.FilledButton("データ取得", icon=ft.Icons.DOWNLOAD, on_click=shelf_download)]),
                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Divider(),
                        ft.Column(controls=[shelf], scroll=ft.ScrollMode.AUTO, expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
                   ]),
            ),
        ],
    )
    
    page.add(tab)

    isbn.focus()
    text.focus()

    # ページを更新
    page.update()

    page.close(dialog_wait)

def login_booklog():
    options = webdriver.ChromeOptions()
    options.set_capability('pageLoadStrategy', 'eager')
    # options.add_argument("--headless")
    # options.add_argument("--window-size=1200x1000")

    driver = webdriver.Chrome(options = options)
    driver.implicitly_wait(1)
    return driver

    driver.get("https://booklog.jp/login")

    e = driver.find_element(By.ID, "account")
    e.clear()
    e.send_keys(config["username"])
    time.sleep(0.1)
    e = driver.find_element(By.ID, "password")
    e.clear()
    e.send_keys(config["password"])
    time.sleep(1)

    # フォームを送信
    button = driver.find_element(By.ID, "login_submit_button")
    driver.execute_script("arguments[0].click();", button)
    time.sleep(0.1)
    button.click() # <- これだけだと不正検知に引っ掛かるので上の行でイベントを発火させる

    while driver.current_url == "https://booklog.jp/login":
        time.sleep(1)

    return driver

def update_category(driver):
    driver.get("https://booklog.jp/users/{}".format(config["username"]))
    driver.find_element(By.CLASS_NAME, "shelf-header-menu-category-modal").click()
    links = driver.find_elements(By.XPATH, "//*[@id='categories']/*/a")
    categories = []
    for link in links:
        r = re.search(r'\?category_id=([0-9a-z]+)', link.get_attribute('href'))
        key = r.group(1)
        if key == 'none': key = "0"
        r = re.search(r' \(([0-9]+)\)', link.text)
        categories.append({"key": key, "text": link.text.replace(r.group(), ''), "count": int(r.group(1))})
    driver.find_element(By.CLASS_NAME, "modal-close").click()
    return categories

def update_dropdown(categories, drop_simple, drop_detail):
    drop_simple.options.clear()
    drop_detail.options.clear()
    for c in categories:
        drop_simple.options.append(ft.dropdown.Option(key=c["key"], text="{} ({})".format(c["text"], c["count"])))
        drop_detail.options.append(ft.dropdown.Option(key=c["key"], text="{} ({})".format(c["text"], c["count"])))

def verify_asin(asin):
    return True if re.match(r'^[0-9]{9}[0-9X]$', asin) else False

def process_text(func, text):
    def process_line(line):
        i = line.split("\t")[0]
        if i.startswith("https://"):
            i = i.split("/")[-1]
        elif re.match(r'^[0-9X]{12}[0-9X]$', i):
            i = isbn_to_asin(i)
        ret = func(i)
        return Success(ret) if ret else Failure(line)
    return map(process_line, [line for line in text.split("\n") if line.strip()])

def isbn_to_asin(isbn):
    asin = isbn[:-1][3:]
    value = int(asin)
    digit = 2
    check = 0
    for i in range(9):
        check += (value % 10) * digit
        value = int(value / 10)
        digit += 1
    check = 11 - (check % 11)
    if check == 10: asin = asin + "X"
    elif check == 11: asin = asin + "0"
    else: asin = asin + str(check)
    return asin

def get_book_info(driver, asin):
    driver.get("https://booklog.jp/edit/1/{}".format(asin))
    title = driver.find_element(By.CLASS_NAME, "titleLink").text
    author = driver.find_element(By.CLASS_NAME, "item-info-author").text
    try:
        category = Select(driver.find_element(By.NAME, "category_id")).all_selected_options[0].text
    except:
        category = "未登録"
    return { "asin": asin, "title": title, "author": author, "category": category }

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
