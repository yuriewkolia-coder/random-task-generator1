class ConsoleView:
    """Класс для взаимодействия с пользователем."""
    @staticmethod
    def show_menu():
        print("\n===== Book Tracker =====")
        print("1. Показать все книги")
        print("2. Добавить книгу")
        print("3. Редактировать книгу")
        print("4. Удалить книгу")
        print("5. Фильтр по жанру")
        print("6. Фильтр по количеству страниц")
        print("7. Отменить последнее действие (Undo)")
        print("8. Показать историю действий")
        print("0. Выход")

    @staticmethod
    def show_books(books):
        if not books:
            print("Список книг пуст.")
            return
        print("\nСписок книг:")
        for i, book in enumerate(books, 1):
            print(f"{i}. {book}")

    @staticmethod
    def get_user_choice(prompt="Ваш выбор: "):
        return input(prompt).strip()

    @staticmethod
    def input_nonempty(prompt):
        while True:
            value = input(prompt).strip()
            if value:
                return value
            print("Ошибка: значение не может быть пустым. Попробуйте снова.")

    @staticmethod
    def input_positive_int(prompt):
        while True:
            try:
                value = int(input(prompt))
                if value > 0:
                    return value
                print("Число должно быть положительным.")
            except ValueError:
                print("Ошибка: введите целое число.")

    @staticmethod
    def show_message(msg):
        print(msg)

    @staticmethod
    def show_history(history):
        if not history:
            print("История пуста.")
            return
        print("\nПоследние действия:")
        for entry in history:
            print(f"- {entry}")