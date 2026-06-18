"""
File-level: Instructions to resolve Railway build/runtime issues
including pydantic / Python version mismatch and keyboard fix.
"""

1) Проблема с ReplyKeyboardMarkup -> ValidationError
   - Ошибка возникает, потому что ReplyKeyboardMarkup ожидает объекты KeyboardButton
     (или словари), а не plain strings.
   - Решение: используйте helper main_menu_keyboard из backend/src/keyboard.py
     и замените вызовы, например:

       # старое (неправильно)
       # await message.answer(text, reply_markup=ReplyKeyboardMarkup(keyboard=kb, ...))
       # где kb — список строк

       # новое (правильно)
       from backend.src.keyboard import main_menu_keyboard
       await message.answer(text, reply_markup=main_menu_keyboard(lang))

   - Найдите в коде функцию main_menu_keyboard или место, где формируется kb,
     и замените на вызов из нового модуля. Если функция уже есть внутри bot.py,
     скорректируйте её, чтобы использовать KeyboardButton.

2) Проблема pydantic / Python 3.13
   В логах видно, что сборка pydantic-core не проходит для Python 3.13.
   Два безопасных варианта:

   A) Рекомендуемый (на уровне деплоя): зафиксировать Python 3.12 в Railway
      - В Railway Project Settings указать Runtime / Python Version = 3.12 (или
        использовать Dockerfile с FROM python:3.12-slim).
      - После переключения перезапустить деплой.

   B) Альтернатива (в коде): обновить/прибить pydantic в requirements (уже добавлено)
      - В backend/requirements.txt добавлен pydantic>=2.9.0.
      - Однако иногда pydantic-core все равно требует перекомпиляции C-расширений;
        если Railway использует несовместимую окружение/группу wheel, лучше вариант A.

3) Что сделать прямо сейчас (шаги)
   - В коде бота заменить формирование reply_markup на использование backend/src/keyboard.main_menu_keyboard.
   - В Railway:
     * Либо выставить Python 3.12 у сервиса (Project / Service settings -> Runtime)
     * Либо попробовать перезапустить билд с обновлённым requirements (мы добавили pydantic>=2.9.0),
       но если сборка всё равно упадёт — вернуться к варианту с 3.12.

4) Если хочешь — могу:
   - Сделать patch/replace в bot.py, чтобы он импортировал и использовал main_menu_keyboard автоматически.
   - Составить Dockerfile на python:3.12, чтобы гарантированно использовать 3.12 в Railway.
