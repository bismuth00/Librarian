import requests
import json

def get_book_from_google_books(isbn):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data['totalItems'] > 0:
            book = data['items'][0]['volumeInfo']
            
            title = book.get('title', 'N/A')
            authors = book.get('authors', ['N/A'])
            publisher = book.get('publisher', 'N/A')
            published_date = book.get('publishedDate', 'N/A')
            
            print(f"タイトル: {title}")
            print(f"著者: {', '.join(authors)}")
            print(f"出版社: {publisher}")
            print(f"出版日: {published_date}")
            
            return book
        else:
            print("書籍が見つかりませんでした")
            return None
            
    except Exception as e:
        print(f"エラー: {e}")
        return None

# 使用例
isbn = "9784873119038"
book_info = get_book_from_google_books(isbn)

# from isbnlib import meta, cover

# def get_book_info_by_isbn(isbn):
#     try:
#         # 書籍のメタデータを取得
#         book_info = meta(isbn)
        
#         if book_info:
#             print(book_info)
#             print(f"タイトル: {book_info.get('Title', 'N/A')}")
#             print(f"著者: {', '.join(book_info.get('Authors', []))}")
#             print(f"出版社: {book_info.get('Publisher', 'N/A')}")
#             print(f"出版年: {book_info.get('Year', 'N/A')}")
#             print(f"ISBN-13: {book_info.get('ISBN-13', 'N/A')}")
            
#             # 表紙画像URLを取得（オプション）
#             cover_url = cover(isbn)
#             if cover_url:
#                 print(f"表紙画像: {cover_url}")
                
#         return book_info
#     except Exception as e:
#         print(f"エラー: {e}")
#         return None

# # 使用例
# isbn = "9784873119038"  # 例：オライリーの本
# isbn = "9784065393758"  # 例：オライリーの本
# book_info = get_book_info_by_isbn(isbn)

# class Test(ft.Container):
#     def __init__(self, page):
#         super().__init__()
#         self.page = page

#     def build(self):
#         self.categories_detail = ft.Dropdown(label="カテゴリ", value="0")
#         self.categories_detail.options.append(
#             ft.dropdown.Option(key=0, text="未設定(188)")
#         )
#         self.categories_detail.options.append(
#             ft.dropdown.Option(key=1, text="20F本棚F-6(0)")
#         )
#         content = ft.Column(
#             controls=[
#                 ft.Text("キーボードを押してみてください"),
#                 self.categories_detail,
#                 ft.FilledButton(
#                     "カメラ",
#                     col=1,
#                     icon=ft.Icons.COPY,
#                     on_click=lambda e: self.update_cat(),
#                 ),
#             ]
#         )

#         self.content = ft.Tabs(
#             is_secondary=True,
#             animation_duration=200,
#             expand=True,
#             tabs=[
#                 ft.Tab(
#                     text="私物漫画管理",
#                     icon=ft.Icons.BOOK,
#                     content=content,
#                 ),
#                 ft.Tab(
#                     text="会社資料管理",
#                     icon=ft.Icons.BUSINESS,
#                     content=ft.Text(f"ttttttttt"),
#                 ),
#             ],
#         )

#     def update_cat(self):
#         self.categories_detail.options.clear()
#         self.categories_detail.options.append(
#             ft.dropdown.Option(key=0, text="未設定(187)")
#         )
#         self.categories_detail.options.append(
#             ft.dropdown.Option(key=1, text="20F本棚F-6(1)")
#         )
#         self.categories_detail.options.append(
#             ft.dropdown.Option(
#                 key=len(self.categories_detail.options),
#                 text=f"len={len(self.categories_detail.options)}",
#             )
#         )
#         self.page.update()


# def main(page: ft.Page):
#     test = Test(page)
#     tabs = ft.Tabs(
#         animation_duration=200,
#         expand=True,
#         tabs=[
#             ft.Tab(
#                 text="私物漫画管理",
#                 icon=ft.Icons.BOOK,
#                 content=test,
#             ),
#             ft.Tab(
#                 text="会社資料管理",
#                 icon=ft.Icons.BUSINESS,
#                 content=ft.Text(f"ttttttttt"),
#             ),
#         ],
#     )

#     page.add(tabs)

#     dialog_wait = ft.AlertDialog(modal=True, title=ft.Text(""))

#     def on_key(e):
#         with util.OpenDialog(page, dialog_wait, "処理中…"):
#             print(f"key: {e.key}")
#             test.update_cat()
#             # categories_detail = ft.Dropdown(label="カテゴリ", value="0")
#             # categories_detail.options.append(ft.dropdown.Option(key=0, text="未設定(187)"))
#             # categories_detail.options.append(ft.dropdown.Option(key=1, text="20F本棚F-6(1)"))
#             # categories_detail.value = 99999
#             page.update()
#             time.sleep(1)
#         # categories_detail.options.pop()
#         # categories_detail.value = 0
#         # page.update()

#     page.on_keyboard_event = on_key
#     page.update()


# ft.app(target=main)
