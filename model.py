from abc import ABC, abstractmethod
from collections import deque
import json
import os


class Book:
    """Модель книги с инкапсуляцией полей."""
    def __init__(self, title: str, author: str, genre: str, pages: int):
        self._title = title
        self._author = author
        self._genre = genre
        self._pages = pages

    @property
    def title(self):
        return self._title

    @property
    def author(self):
        return self._author

    @property
    def genre(self):
        return self._genre

    @property
    def pages(self):
        return self._pages

    def to_dict(self):
        return {
            "title": self.title,
            "author": self.author,
            "genre": self.genre,
            "pages": self.pages
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["title"], data["author"], data["genre"], data["pages"])

    def __str__(self):
        return f'"{self.title}" — {self.author}, жанр: {self.genre}, {self.pages} стр.'


class Command(ABC):
    """Базовый класс для команд (полиморфизм)."""
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def undo(self):
        pass


class AddBookCommand(Command):
    def __init__(self, repository, book):
        self.repository = repository
        self.book = book

    def execute(self):
        self.repository._books.append(self.book)
        self.repository._save()

    def undo(self):
        self.repository._books.remove(self.book)
        self.repository._save()


class DeleteBookCommand(Command):
    def __init__(self, repository, index):
        self.repository = repository
        self.index = index
        self.removed_book = None

    def execute(self):
        if 0 <= self.index < len(self.repository._books):
            self.removed_book = self.repository._books.pop(self.index)
            self.repository._save()
            return self.removed_book
        return None

    def undo(self):
        if self.removed_book:
            self.repository._books.insert(self.index, self.removed_book)
            self.repository._save()


class EditBookCommand(Command):
    def __init__(self, repository, index, new_title=None, new_author=None,
                 new_genre=None, new_pages=None):
        self.repository = repository
        self.index = index
        self.new_title = new_title
        self.new_author = new_author
        self.new_genre = new_genre
        self.new_pages = new_pages
        self.old_state = None

    def execute(self):
        if 0 <= self.index < len(self.repository._books):
            book = self.repository._books[self.index]
            self.old_state = {
                "title": book.title,
                "author": book.author,
                "genre": book.genre,
                "pages": book.pages
            }
            if self.new_title is not None:
                book._title = self.new_title
            if self.new_author is not None:
                book._author = self.new_author
            if self.new_genre is not None:
                book._genre = self.new_genre
            if self.new_pages is not None:
                book._pages = self.new_pages
            self.repository._save()
            return book
        return None

    def undo(self):
        if self.old_state and 0 <= self.index < len(self.repository._books):
            book = self.repository._books[self.index]
            book._title = self.old_state["title"]
            book._author = self.old_state["author"]
            book._genre = self.old_state["genre"]
            book._pages = self.old_state["pages"]
            self.repository._save()


class BookRepository:
    """Хранилище книг с операциями и историей действий."""
    def __init__(self, json_path="books.json"):
        self._json_path = json_path
        self._books = []
        self._command_stack = deque()      # Стек для undo (LIFO)
        self._action_history = deque()     # Очередь для истории (FIFO)
        self._load()

    @property
    def books(self):
        return list(self._books)   # возвращаем копию для безопасности

    def add_book(self, title, author, genre, pages):
        book = Book(title, author, genre, pages)
        cmd = AddBookCommand(self, book)
        cmd.execute()
        self._command_stack.append(cmd)
        self._action_history.append(f"Добавлена: {book}")

    def delete_book(self, index):
        cmd = DeleteBookCommand(self, index)
        book = cmd.execute()
        if book:
            self._command_stack.append(cmd)
            self._action_history.append(f"Удалена: {book}")
            return book
        return None

    def edit_book(self, index, title=None, author=None, genre=None, pages=None):
        cmd = EditBookCommand(self, index, title, author, genre, pages)
        book = cmd.execute()
        if book:
            self._command_stack.append(cmd)
            self._action_history.append(f"Изменена: {book}")
            return book
        return None

    def undo_last_action(self):
        if self._command_stack:
            cmd = self._command_stack.pop()
            cmd.undo()
            self._action_history.append(f"Отмена действия: {type(cmd).__name__}")
            return True
        return False

    def get_history(self, count=None):
        """Возвращает историю действий (последние count записей)."""
        if count is None:
            return list(self._action_history)
        history = list(self._action_history)
        return history[-count:] if count > 0 else []

    def filter_by_genre(self, genre):
        return [b for b in self._books if b.genre.lower() == genre.lower()]

    def filter_by_pages(self, min_pages=None, max_pages=None):
        result = self._books
        if min_pages is not None:
            result = [b for b in result if b.pages >= min_pages]
        if max_pages is not None:
            result = [b for b in result if b.pages <= max_pages]
        return result

    def _load(self):
        if os.path.exists(self._json_path):
            with open(self._json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._books = [Book.from_dict(item) for item in data]
        else:
            self._books = []
            self._save()

    def _save(self):
        with open(self._json_path, "w", encoding="utf-8") as f:
            json.dump([book.to_dict() for book in self._books], f,
                      ensure_ascii=False, indent=2)