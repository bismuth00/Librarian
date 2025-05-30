import time
import re
import os
import json
from returns.result import Failure, Success
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import flet as ft

STATE_UNKNOWN_KEY = "unknown"
STATE_UNKNOWN_VALUE = "所在不明"
STATE_CHECKED_KEY = "checked"
STATE_CHECKED_VALUE = "確認済み"
STATE_ADD_KEY = "add"
STATE_ADD_VALUE = "新規追加"
STATE_DICT = {
    STATE_UNKNOWN_KEY: STATE_UNKNOWN_VALUE,
    STATE_CHECKED_KEY: STATE_CHECKED_VALUE,
    STATE_ADD_KEY: STATE_ADD_VALUE,
}


def login_booklog(config):
    options = webdriver.ChromeOptions()
    options.set_capability("pageLoadStrategy", "eager")
    # options.add_argument("--headless")
    # options.add_argument("--window-size=1200x1000")

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(0)

    if os.path.exists("cookies.json"):
        driver.get("https://booklog.jp/users/{}".format(config["username"]))
        with open("cookies.json", "r", encoding="utf-8") as f:
            cookies = json.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
    else:
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
        button.click()  # <- これだけだと不正検知に引っ掛かるので上の行でイベントを発火させる

        while driver.current_url == "https://booklog.jp/login":
            time.sleep(1)

        driver.get("https://booklog.jp/users/{}".format(config["username"]))
        with open("cookies.json", "w", encoding="utf-8") as f:
            json.dump(driver.get_cookies(), f, ensure_ascii=False, indent=2)

    return driver


def verify_asin(asin):
    return True if re.match(r"^[0-9]{9}[0-9X]$", asin) else False


def process_text(func, text):
    def process_line(line):
        i = line.split("\t")[0]
        if i.startswith("https://"):
            i = i.split("/")[-1]
        elif re.match(r"^[0-9X]{12}[0-9X]$", i):
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
    if check == 10:
        asin = asin + "X"
    elif check == 11:
        asin = asin + "0"
    else:
        asin = asin + str(check)
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
        category = (
            Select(driver.find_element(By.NAME, "category_id"))
            .all_selected_options[0]
            .text
        )
        tags = driver.find_element(By.ID, "tags").text
    except:
        category = "未登録"
        tags = ""
    return {
        "asin": asin,
        "title": title,
        "author": author,
        "category": category,
        "tags": tags,
    }


def get_book_categories(driver, config):
    driver.get("https://booklog.jp/users/{}".format(config["username"]))
    driver.find_element(By.CLASS_NAME, "shelf-header-menu-category-modal").click()
    links = driver.find_elements(By.XPATH, "//*[@id='categories']/*/a")
    categories = []
    for link in links:
        r = re.search(r"\?category_id=([0-9a-z]+)", link.get_attribute("href"))
        key = r.group(1)
        if key == "none":
            key = "0"
        r = re.search(r" \(([0-9]+)\)", link.text)
        categories.append(
            {
                "key": key,
                "text": link.text.replace(r.group(), ""),
                "count": int(r.group(1)),
            }
        )
    driver.find_element(By.CLASS_NAME, "modal-close").click()
    return categories


def create_dropdown_location(categories):
    dropdown = ft.Dropdown(label="場所", value="0")
    for c in categories:
        dropdown.options.append(
            ft.dropdown.Option(
                key=c["key"], text="{} ({})".format(c["text"], c["count"])
            )
        )
    return dropdown


def update_dropdown_location(dropdown, categories, page):
    value = dropdown.value
    dropdown.options.clear()
    for c in categories:
        dropdown.options.append(
            ft.dropdown.Option(
                key=c["key"], text="{} ({})".format(c["text"], c["count"])
            )
        )
    dropdown.options.append(ft.dropdown.Option(key=-1, text=" "))
    dropdown.value = -1
    page.update()
    time.sleep(0.005)
    dropdown.options.pop()
    dropdown.value = value
    page.update()


class OpenWaitDialog:
    def __init__(self, page, title):
        self.dialog = ft.AlertDialog(modal=True, title=ft.Text(title))
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
        actions=[ft.TextButton("閉じる", on_click=lambda e: page.close(dialog))],
    )
    page.open(dialog)
