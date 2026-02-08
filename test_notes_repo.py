"""
Тестирование репозитория заметок.
Запустите: python test_notes_repo.py
"""
from app.repositories.notes import get_notes_repository


def test_repository():
    # Получаем репозиторий (автоматически выберет реализацию)
    repo = get_notes_repository()
    print(f"Используется репозиторий: {type(repo).__name__}")
    print("-" * 60)

    # Тест 1: Создание заметки
    print("Тест 1: Создание заметки")
    note1 = repo.create_note(todo_id=1, text="Первая заметка", is_public=True)
    print(f"  Создана заметка: {note1}")
    assert note1["text"] == "Первая заметка"
    assert note1["todo_id"] == 1
    assert note1["is_public"] is True
    print("   Успешно")
    print()

    # Тест 2: Создание приватной заметки
    print("Тест 2: Создание приватной заметки")
    note2 = repo.create_note(todo_id=2, text="Приватная заметка", is_public=False)
    print(f"  Создана заметка: {note2}")
    assert note2["is_public"] is False
    print("   Успешно")
    print()

    # Тест 3: Список всех заметок
    print("Тест 3: Список всех заметок")
    all_notes = repo.list_notes()
    print(f"  Найдено заметок: {len(all_notes)}")
    assert len(all_notes) == 2
    print("   Успешно")
    print()

    # Тест 4: Фильтр по задаче
    print("Тест 4: Фильтр по задаче (todo_id=1)")
    filtered = repo.list_notes(todo_id=1)
    print(f"  Найдено заметок для задачи 1: {len(filtered)}")
    assert len(filtered) == 1
    assert filtered[0]["todo_id"] == 1
    print("   Успешно")
    print()

    # Тест 5: Только публичные заметки
    print("Тест 5: Только публичные заметки")
    public_notes = repo.list_notes(public_only=True)
    print(f"  Найдено публичных заметок: {len(public_notes)}")
    assert len(public_notes) == 1
    assert public_notes[0]["is_public"] is True
    print("   Успешно")
    print()

    # Тест 6: Получение заметки по ID
    print("Тест 6: Получение заметки по ID")
    retrieved = repo.get_note(note1["id"])
    print(f"  Получена заметка: {retrieved}")
    assert retrieved["id"] == note1["id"]
    assert retrieved["text"] == note1["text"]
    print("   Успешно")
    print()

    # Тест 7: Удаление заметки
    print("Тест 7: Удаление заметки")
    deleted = repo.delete_note(note2["id"])
    print(f"  Удалена заметка {note2['id']}: {deleted}")
    assert deleted is True
    assert repo.get_note(note2["id"]) is None
    print("   Успешно")
    print()

    # Тест 8: Список после удаления
    print("Тест 8: Список после удаления")
    remaining = repo.list_notes()
    print(f"  Осталось заметок: {len(remaining)}")
    assert len(remaining) == 1
    print("   Успешно")
    print()

    print("=" * 60)
    print(" Все тесты пройдены успешно!")
    print("=" * 60)


if __name__ == "__main__":
    test_repository()