import json
from pprint import pp
import flet as ft
import booklog
import cosmos
import util

def main(page: ft.Page):
    config = json.load(open("config.json", "r", encoding="utf-8"))
    page.title = "蔵書管理"
    page.window.width = 1200
    page.window.height = 960
    page.update()
    with util.OpenWaitDialog(page, "初期化中…"):
        tabs = ft.Tabs(
            animation_duration=200,
            expand=True,
            tabs=[
                ft.Tab(
                    text="私物漫画管理",
                    icon=ft.Icons.BOOK,
                    content=booklog.Booklog(page, config),
                ),
                ft.Tab(
                    text="会社資料管理",
                    icon=ft.Icons.BUSINESS,
                    content=cosmos.Cosmos(page dialog_error),
                )
            ])
        page.add(tabs)
        util.window_on_top(page)

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
