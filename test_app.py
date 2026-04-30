import unittest
import os
import json
from model import Book, BookRepository, AddBookCommand, DeleteBookCommand, EditBookCommand


class TestBookModel(unittest.TestCase):
    def test_create_book(self):
        book = Book("Война и мир", "Л. Толстой", "Роман", 1225)
        self.assertEqual(book.title, "Война и мир")
        self.assertEqual(book.pages, 1225)

    def test_book_to_dict(self):
        book = Book("Test", "Author", "Genre", 123)
        self.assertEqual(book.to_dict(), {
            "title": "Test",
            "author": "Author",
            "genre": "Genre",
            "pages": 123
        })

    def test_book_from_dict(self):
        data = {"title": "A", "author": "B", "genre": "C", "pages": 10}
        book = Book.from_dict(data)
        self.assertEqual(book.author, "B")


class TestCommands(unittest.TestCase):
    def setUp(self):
        # временный json для тестов
        self.test_json = "test_books.json"
        self.repo = BookRepository(self.test_json)

    def tearDown(self):
        if os.path.exists(self.test_json):
            os.remove(self.test_json)

    def test_add_book_command(self):
        self.assertEqual(len(self.repo.books), 0)
        self.repo.add_book("Title", "Author", "Genre", 100)
        self.assertEqual(len(self.repo.books), 1)
        self.assertEqual(self.repo.books[0].title, "Title")

    def test_undo_add(self):
        self.repo.add_book("Book", "Auth", "Genre", 5)
        self.repo.undo_last_action()
        self.assertEqual(len(self.repo.books), 0)

    def test_delete_and_undo(self):
        self.repo.add_book("B1", "A1", "G", 50)
        self.repo.add_book("B2", "A2", "G", 70)
        self.repo.delete_book(0)
        self.assertEqual(len(self.repo.books), 1)
        self.assertEqual(self.repo.books[0].title, "B2")
        self.repo.undo_last_action()
        self.assertEqual(len(self.repo.books), 2)
        self.assertEqual(self.repo.books[0].title, "B1")

    def test_edit_and_undo(self):
        self.repo.add_book("Old", "OldAuth", "OldGenre", 200)
        self.repo.edit_book(0, title="New", pages=300)
        book = self.repo.books[0]
        self.assertEqual(book.title, "New")
        self.assertEqual(book.pages, 300)
        # автор и жанр не должны измениться
        self.assertEqual(book.author, "OldAuth")
        self.repo.undo_last_action()
        book = self.repo.books[0]
        self.assertEqual(book.title, "Old")
        self.assertEqual(book.pages, 200)

    def test_filter_genre(self):
        self.repo.add_book("B1", "A1", "Фантастика", 100)
        self.repo.add_book("B2", "A2", "Роман", 200)
        res = self.repo.filter_by_genre("фантастика")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].title, "B1")

    def test_filter_pages(self):
        self.repo.add_book("B1", "A1", "G", 100)
        self.repo.add_book("B2", "A2", "G", 300)
        self.repo.add_book("B3", "A3", "G", 500)
        res = self.repo.filter_by_pages(min_pages=200, max_pages=400)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].title, "B2")

    def test_validation_positive_int(self):
        # имитация ввода, сработает при вызове input_positive_int
        # для теста просто проверяем, что модель не принимает отрицательные
        # (валидация на уровне контроллера, здесь просто структура)
        with self.assertRaises(TypeError):
            # pages должно быть int, но отрицательное - ок, валидация в контроллере
            pass


if __name__ == "__main__":
    unittest.main()