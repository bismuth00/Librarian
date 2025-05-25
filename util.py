# -*- coding: utf-8 -*-

import time
import re

from returns.result import Failure, Success

from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

import flet as ft

STATE_UNKNOWN_KEY = "unknown"
STATE_UNKNOWN_VALUE = "所在不明"
STATE_CHECKED_KEY = "checked"
STATE_CHECKED_VALUE = "確認済み"
STATE_DICT = {STATE_UNKNOWN_KEY:STATE_UNKNOWN_VALUE, STATE_CHECKED_KEY:STATE_CHECKED_VALUE, "add":"新規追加"}

def update_dropdown(categories, drop_simple, drop_detail):
    drop_simple.options.clear()
    drop_detail.options.clear()
    for c in categories:
        drop_simple.options.append(ft.dropdown.Option(key=c["key"], text="{}".format(c["text"])))
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

def window_on_top(page):
    page.window.always_on_top = True
    page.update()
    time.sleep(0.2)
    page.window.always_on_top = False
    page.update()

def get_book_info(driver, asin):
    driver.get("https://booklog.jp/edit/1/{}".format(asin))
    title = driver.find_element(By.CLASS_NAME, "titleLink").text
    author = driver.find_element(By.CLASS_NAME, "item-info-author").text
    try:
        category = Select(driver.find_element(By.NAME, "category_id")).all_selected_options[0].text
        tags = driver.find_element(By.ID, "tags").text
    except:
        category = "未登録"
        tags = ""
    return { "asin": asin, "title": title, "author": author, "category": category, "tags": tags }

class OpenWaitDialog:
    def __init__(self, page, title):
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title))
        self.page = page
    def __enter__(self):
        self.page.open(self.dialog)
    def __exit__(self, exc_type, exc_value, traceback):
        self.page.close(self.dialog)

def OpenErrorDialog(page, title):
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(title),
        content=ft.Text(""),
        actions=[ft.TextButton("閉じる", on_click=lambda e: page.close(dialog))]
    )
    page.open(dialog)
