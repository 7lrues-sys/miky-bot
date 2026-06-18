"""
File-level: aiogram handlers and FSM states for Mikky backend.
Contains onboarding, language selection, timezone capture and 'new task' FSM.
"""

import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram import Bot
from typing import List, Dict, Any
import json
from .db import fetchrow, execute

router = Router()

class NewTaskStates(StatesGroup):
    """
    FSM states for creating a new task.
    """
    waiting_for_content = State()

# Simple list of language codes for the picker (extend as needed).
LANGUAGES: List[Dict[str, str]] = [
    {"code": "en", "label": "English"},
    {"code": "ru", "label": "Русский"},
    {"code": "uk", "label": "Українська"},
    {"code": "es", "label": "Español"},
    {"code": "fr", "label": "Français"},
    {"code": "pt", "label": "Português"}
    # Add remaining language codes (total 21) in production.
]

def build_language_keyboard():
    """
    Build a simple inline keyboard for language selection.
    """
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(row_width=3)
    for lang in LANGUAGES:
        kb.insert(InlineKeyboardButton(text=lang["label"], callback_data=f"lang:{lang['code']}"))
    return kb

@router.message(Command("start"))
async def cmd_start(message: Message):
    """
    Handle /start: show Terms and accept buttons and block further actions until accepted.
    """
    text = (
        "Welcome to Mikky — your smart planner.\n\n"
        "Before we start, please read and accept the Terms of Service and Privacy Policy.\n"
    )
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Принимаю ✅", callback_data="accept_terms"),
            InlineKeyboardButton(text="Не согласен ❌", callback_data="decline_terms")
        ]
    ])
    await message.answer(text, reply_markup=kb)

@router.callback_query(lambda c: c.data == "decline_terms")
async def on_decline_terms(callback: CallbackQuery):
    """
    User declined terms -> inform and stop.
    """
    await callback.answer("Нельзя использовать бота без принятия условий.", show_alert=True)

@router.callback_query(lambda c: c.data == "accept_terms")
async def on_accept_terms(callback: CallbackQuery):
    """
    User accepted terms -> create or update user row and prompt language selection.
    """
    tg_id = callback.from_user.id
    # Insert user if not exists or update terms_accepted
    await execute(
        "INSERT INTO users (telegram_id, terms_accepted, accepted_at) VALUES ($1, TRUE, NOW()) "
        "ON CONFLICT (telegram_id) DO UPDATE SET terms_accepted = TRUE, accepted_at = NOW()",
        tg_id
    )
    await callback.message.answer("Спасибо! Выберите язык интерфейса:", reply_markup=build_language_keyboard())
    await callback.answer()

@router.callback_query(lambda c: c.data and c.data.startswith("lang:"))
async def on_language_selected(callback: CallbackQuery):
    """
    Save selected language and prompt for timezone (simple text prompt).
    """
    code = callback.data.split(":", 1)[1]
    tg_id = callback.from_user.id
    await execute("UPDATE users SET language=$1 WHERE telegram_id=$2", code, tg_id)
    await callback.message.answer(f"Язык установлен: {code}\nПожалуйста, отправьте ваш часовой пояс (например Europe/Kiev) или нажмите 'Отправить геопозицию' в клиенте.")
    await callback.answer()

@router.message(lambda message: message.text and message.text.startswith("Europe"))
async def on_timezone_text(message: Message):
    """
    Very small timezone capture: user can type timezone identifier.
    """
    tz = message.text.strip()
    tg_id = message.from_user.id
    await execute("UPDATE users SET timezone=$1 WHERE telegram_id=$2", tz, tg_id)
    await message.answer("Спасибо! Настройка завершена. Чтобы создать новую задачу — нажмите /newtask")

@router.message(Command("newtask"))
async def cmd_newtask(message: Message, state: FSMContext):
    """
    Start 'new task' FSM.
    """
    await state.set_state(NewTaskStates.waiting_for_content)
    await message.answer("Пришлите текст, фото, ссылку или голосовое сообщение для задачи.\nЕсли нужен пример: 'Завтра кофе с Леной 15:00'")

@router.message(NewTaskStates.waiting_for_content, F.content_type.in_({"text", "voice", "photo"}))
async def handle_newtask_content(message: Message, state: FSMContext):
    """
    Receive the content for a new task, create a DB row and trigger background processing.
    Heavy AI parsing should be delegated to a worker — here we just store raw text / placeholder.
    """
    tg_id = message.from_user.id

    # Resolve user id in our users table
    user_row = await fetchrow("SELECT id FROM users WHERE telegram_id=$1", tg_id)
    if not user_row:
        await message.answer("Пользователь не найден. Пожалуйста, выполните /start и примите условия.")
        await state.clear()
        return

    user_db_id = user_row["id"]

    if message.text:
        raw_text = message.text
    elif message.voice:
        # For MVP we store a placeholder and plan to process in worker.
        raw_text = f"<voice file_id={message.voice.file_id}>"
        # Optionally store media reference in media_archive
        await execute("INSERT INTO media_archive (user_id, file_id, status) VALUES ($1,$2,$3)",
                      user_db_id, message.voice.file_id, "pending")
    elif message.photo:
        # take highest resolution
        file_id = message.photo[-1].file_id
        raw_text = f"<photo file_id={file_id}>"
        await execute("INSERT INTO media_archive (user_id, file_id, status) VALUES ($1,$2,$3)",
                      user_db_id, file_id, "pending")
    else:
        raw_text = "<unsupported content>"

    # Insert a task with NULL deadline: AI worker will attempt to parse and update.
    await execute(
        "INSERT INTO tasks (user_id, task_text, deadline, status) VALUES ($1,$2,NULL,'active')",
        user_db_id, raw_text
    )

    await message.answer("Задача сохранена! Я попробую распознать дату/время в фоне. Если нужно — укажи вручную.")
    await state.clear()

# Admin helper endpoints (callback protected by ADMIN_TOKEN) could be added here in production.
