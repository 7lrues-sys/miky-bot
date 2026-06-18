"""
File-level: Utility for building Telegram keyboards used by the bot.
This module provides helper functions that return properly typed
aiogram ReplyKeyboardMarkup and KeyboardButton objects.
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from typing import List

def _make_buttons(rows: List[List[str]]) -> List[List[KeyboardButton]]:
    """
    Создает структуру KeyboardButton из вложенного списка строк.

    :param rows: Список строк кнопок, где каждая внутренняя
                 последовательность — ряд клавиатуры.
    :return: Список списков KeyboardButton.
    """
    return [[KeyboardButton(text=cell) for cell in row] for row in rows]

def main_menu_keyboard(lang: str = "uk") -> ReplyKeyboardMarkup:
    """
    Возвращает основное меню бота (ReplyKeyboardMarkup) в виде
    набора KeyboardButton. Используй эту функцию вместо передачи
    простых строк в ReplyKeyboardMarkup.

    :param lang: Языковой код (пока используется для возможной
                 локализации текста кнопок в будущем).
    :return: ReplyKeyboardMarkup с корректными объектами KeyboardButton.
    """
    # TODO: при необходимости добавить локализацию по lang
    rows = [
        ["➕ Нова задача", "📅 На сьогодні"],
        ["📅 На завтра", "📅 На тиждень"],
        ["📅 На місяць", "❓ Не зроблено"],
        ["✅ Зроблено", "📋 Всі задачі"],
    ]

    kb = _make_buttons(rows)
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, persistent=True)
