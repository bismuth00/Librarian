import json
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
                    content=cosmos.Cosmos(page),
                )
            ])
        page.add(tabs)
        util.window_on_top(page)

ft.app(target=main)
