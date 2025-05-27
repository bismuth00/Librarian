import json
import os
from google.cloud import firestore


class Firestone:
    def __init__(self):
        self.categories = set()
        self.locations = set()
        self.classes = set()
        self.books = {}

        with open("books.json", "r", encoding="utf-8") as f:
            self.books = json.load(f)

        # サービスアカウントキーのパスを環境変数で指定
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "firebase.json"

        # クライアント作成
        self.db = firestore.Client()

        docs = self.db.collection("books").stream()
        for doc in docs:
            self.books[doc.id] = doc.to_dict()

        # for _, book in self.books.items():
        #     if "category" in book:
        #         self.categories.add(book["category"])
        #     if "location" in book:
        #         self.locations.add(book["location"])
        #     c = book["class_id"].split("-")
        #     if len(c) == 2 and not c[0].isdigit():
        #         self.classes.add(c[0])

        # print("Categories:", self.categories)
        # print("Locations:", self.locations)
        # print("Classes:", self.classes)

        # with open("books.json", "w", encoding="utf-8") as f:
        #     json.dump(self.books, f, ensure_ascii=False, indent=2)


f = Firestone()
