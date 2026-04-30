from model import BookRepository
from view import ConsoleView


class BookController:
    def __init__(self):
        self.repository = BookRepository()
        self.view = ConsoleView()

    def run(self):
        while True:
            self.view.show_menu()
            choice = self.view.get_user_choice()
            if choice == "1":
                self._show_all()
            elif choice == "2":
                self._add_book()
            elif choice == "3":
                self._edit_book()
            elif choice == "4":
                self._delete_book()
            elif choice == "5":
                self._filter_by_genre()
            elif choice == "6":
                self._filter_by_pages()
            elif choice == "7":
                self._undo()
            elif choice == "8":
                self._show_history()
            elif choice == "0":
                print("До свидания!")
                break
            else:
                self.view.show_message("Неверный пункт меню. Попробуйте снова.")

    def _show_all(self):
        self.view.show_books(self.repository.books)

    def _add_book(self):
        print("\nДобавление новой книги:")
        title = self.view.input_nonempty("Название: ")
        author = self.view.input_nonempty("Автор: ")
        genre = self.view.input_nonempty("Жанр: ")
        pages = self.view.input_positive_int("Количество страниц: ")
        self.repository.add_book(title, author, genre, pages)
        self.view.show_message("Книга добавлена.")

    def _edit_book(self):
        books = self.repository.books
        if not books:
            self.view.show_message("Список книг пуст. Редактировать нечего.")
            return
        self.view.show_books(books)
        try:
            idx = int(self.view.get_user_choice("Введите номер книги для редактирования: ")) - 1
            if idx < 0 or idx >= len(books):
                self.view.show_message("Неверный номер.")
                return
        except ValueError:
            self.view.show_message("Ошибка: введите число.")
            return

        book = books[idx]
        print(f"Редактирование: {book}")
        print("Оставьте поле пустым, чтобы сохранить текущее значение.")
        title = input("Новое название: ").strip()
        author = input("Новый автор: ").strip()
        genre = input("Новый жанр: ").strip()
        pages_str = input("Новое количество страниц: ").strip()

        # Проверка страниц, если введены
        new_title = title if title else None
        new_author = author if author else None
        new_genre = genre if genre else None
        new_pages = None
        if pages_str:
            try:
                new_pages = int(pages_str)
                if new_pages <= 0:
                    self.view.show_message("Количество страниц должно быть положительным. Изменение не применено.")
                    return
            except ValueError:
                self.view.show_message("Ошибка: введите целое число для страниц. Изменение не применено.")
                return

        updated = self.repository.edit_book(idx, new_title, new_author, new_genre, new_pages)
        if updated:
            self.view.show_message("Книга обновлена.")
        else:
            self.view.show_message("Не удалось обновить книгу.")

    def _delete_book(self):
        books = self.repository.books
        if not books:
            self.view.show_message("Список книг пуст. Удалять нечего.")
            return
        self.view.show_books(books)
        try:
            idx = int(self.view.get_user_choice("Введите номер книги для удаления: ")) - 1
            if idx < 0 or idx >= len(books):
                self.view.show_message("Неверный номер.")
                return
        except ValueError:
            self.view.show_message("Ошибка: введите число.")
            return

        book = self.repository.delete_book(idx)
        if book:
            self.view.show_message(f"Книга удалена: {book}")
        else:
            self.view.show_message("Не удалось удалить книгу.")

    def _filter_by_genre(self):
        genre = self.view.input_nonempty("Введите жанр для поиска: ")
        result = self.repository.filter_by_genre(genre)
        self.view.show_books(result)

    def _filter_by_pages(self):
        min_str = self.view.get_user_choice("Минимальное количество страниц (Enter - без ограничения): ")
        max_str = self.view.get_user_choice("Максимальное количество страниц (Enter - без ограничения): ")
        min_pages = int(min_str) if min_str else None
        max_pages = int(max_str) if max_str else None
        result = self.repository.filter_by_pages(min_pages, max_pages)
        self.view.show_books(result)

    def _undo(self):
        if self.repository.undo_last_action():
            self.view.show_message("Последнее действие отменено.")
        else:
            self.view.show_message("Нет действий для отмены.")

    def _show_history(self):
        # Показываем последние 10 действий
        history = self.repository.get_history(10)
        self.view.show_history(history)