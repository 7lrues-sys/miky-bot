import asyncio
import logging
import sqlite3
import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, 
    CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz

# ==============================
# НАСТРОЙКИ
# ==============================
BOT_TOKEN = "8988206711:AAGmjkJ0t-hz0iU1cDmIgsXK9sXvxk6xJzg"
TIMEZONE = pytz.timezone("Europe/Kiev")
TRIAL_DAYS = 7
STAR_PRICE = 300                    # ≈ 99 UAH / 3-4 USD
MONOBANK_URL = "https://send.monobank.ua/jar/5gfL2BGRr3"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler(timezone=TIMEZONE)

# ==============================
# ЯЗЫКИ
# ==============================
LANGUAGES = {
    'en': '🇬🇧 English', 'zh': '🇨🇳 中文 (普通话)', 'hi': '🇮🇳 हिन्दी',
    'es': '🇪🇸 Español', 'fr': '🇫🇷 Français', 'ar': '🇸🇦 العربية',
    'bn': '🇧🇩 বাংলা', 'pt': '🇧🇷 Português', 'ru': '🇷🇺 Русский',
    'ur': '🇵🇰 اردو', 'id': '🇮🇩 Bahasa Indonesia', 'de': '🇩🇪 Deutsch',
    'ja': '🇯🇵 日本語', 'mr': '🇮🇳 मराठी', 'te': '🇮🇳 తెలుగు',
    'tr': '🇹🇷 Türkçe', 'ta': '🇮🇳 தமிழ்', 'wuu': '🇨🇳 吴语',
    'yue': '🇨🇳 粤语', 'vi': '🇻🇳 Tiếng Việt'
}

# ==============================
# ПЕРЕВОДЫ
# ==============================
TRANSLATIONS = {
    'en': {
        'start_hello': "🌟 Hello! I am your new helper *Mikky*! 🌟\n\nChoose your language:",
        'enable_notifications': "🔔 Please enable notifications from the bot!\n\nHow:\n1. Tap ⋮ → Notifications → ON",
        'main_welcome': "Hello! I am your new assistant *Mikky* 🌟\n\nSend me your plans and tasks!",
        'trial_info': "You have 7 days of free access.",
        'payment_title': "Choose payment method:",
        'daily_greeting': "🌅 Good morning, {name}!\n\n**Today's plan:**\n{tasks}\n\n💡 {motivation}"
    },
    'ru': {
        'start_hello': "🌟 Привет! Я твой новый помощник *Mikky*! 🌟\n\nВыбери язык:",
        'enable_notifications': "🔔 Пожалуйста, включи уведомления от бота!",
        'main_welcome': "Привет! Я твой новый помощник *Mikky* 🌟\n\nРасскажи мне о своих планах!",
        'trial_info': "У тебя есть 7 дней бесплатного доступа.",
        'payment_title': "Выбери способ оплаты:",
        'daily_greeting': "🌅 Доброе утро, {name}!\n\n**План на сегодня:**\n{tasks}\n\n💡 {motivation}"
    }
}

# ==============================
# МОТИВАЦИОННЫЕ СООБЩЕНИЯ (добавь все 100)
# ==============================
MESSAGES = [
    "Ты способна на всё, что задумаешь 💫", "Каждый день — новый шанс стать лучше 🌱",
    "Твои мечты заслуживают действий 🚀", "Верь в себя — ты уже на правильном пути ✨",
    # ... вставь остальные ...
    "Всё в твоей жизни складывается правильно 🧩"
]

# ==============================
# БАЗА ДАННЫХ (без изменений)
# ==============================
def init_db():
    conn = sqlite3.connect("mikky.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT,
        language TEXT DEFAULT 'en', is_paid INTEGER DEFAULT 0,
        trial_start TEXT, used_messages TEXT DEFAULT ''
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY, user_id INTEGER, text TEXT,
        event_date TEXT, event_time TEXT, created_at TEXT
    )''')
    conn.commit()
    conn.close()

def create_user(user_id, username, first_name):
    conn = sqlite3.connect("mikky.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, trial_start) VALUES (?,?,?,?)",
              (user_id, username, first_name, datetime.now(TIMEZONE).isoformat()))
    conn.commit()
    conn.close()

def get_user_language(user_id):
    conn = sqlite3.connect("mikky.db")
    c = conn.cursor()
    c.execute("SELECT language FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 'en'

def update_user_language(user_id, lang):
    conn = sqlite3.connect("mikky.db")
    c = conn.cursor()
    c.execute("UPDATE users SET language=? WHERE user_id=?", (lang, user_id))
    conn.commit()
    conn.close()

def get_all_active_users():
    conn = sqlite3.connect("mikky.db")
    c = conn.cursor()
    c.execute("SELECT user_id, first_name, language FROM users")
    rows = c.fetchall()
    conn.close()
    return rows

def save_task(user_id, text, event_date=None, event_time=None):
    conn = sqlite3.connect("mikky.db")
    c = conn.cursor()
    c.execute("INSERT INTO tasks (user_id, text, event_date, event_time, created_at) VALUES (?,?,?,?,?)",
              (user_id, text, event_date, event_time, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_tasks_for_today(user_id):
    today = datetime.now(TIMEZONE).strftime("%Y-%m-%d")
    conn = sqlite3.connect("mikky.db")
    c = conn.cursor()
    c.execute("SELECT text, event_time FROM tasks WHERE user_id=? AND event_date=? ORDER BY event_time", (user_id, today))
    rows = c.fetchall()
    conn.close()
    return rows

def get_tasks_for_week(user_id):
    now = datetime.now(TIMEZONE)
    week_end = now + timedelta(days=7)
    conn = sqlite3.connect("mikky.db")
    c = conn.cursor()
    c.execute("""SELECT text, event_date, event_time FROM tasks 
                 WHERE user_id=? AND event_date >= ? AND event_date <= ? 
                 ORDER BY event_date, event_time""",
              (user_id, now.strftime("%Y-%m-%d"), week_end.strftime("%Y-%m-%d")))
    rows = c.fetchall()
    conn.close()
    return rows

def get_unique_message(user_id):
    conn = sqlite3.connect("mikky.db")
    c = conn.cursor()
    c.execute("SELECT used_messages FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    used = row[0].split(",") if row and row[0] else []
    used = [int(x) for x in used if x]
    available = [i for i in range(len(MESSAGES)) if i not in used]
    if not available:
        available = list(range(len(MESSAGES)))
        used = []
    idx = random.choice(available)
    used.append(idx)
    c.execute("UPDATE users SET used_messages=? WHERE user_id=?", (",".join(map(str, used)), user_id))
    conn.commit()
    conn.close()
    return MESSAGES[idx]

# ==============================
# КЛАВИАТУРЫ
# ==============================
def main_menu_keyboard(lang: str = 'ru'):
    if lang in ['ru', 'uk']:
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="/новая_задача"), KeyboardButton(text="/мои_задачи_на_день")],
            [KeyboardButton(text="/мои_задачи_на_неделю"), KeyboardButton(text="/мои_задачи_на_месяц")],
            [KeyboardButton(text="/просто_сделать"), KeyboardButton(text="/не_сделано")]
        ], resize_keyboard=True, persistent=True)
    else:
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="/new_task"), KeyboardButton(text="/today_tasks")],
            [KeyboardButton(text="/week_tasks"), KeyboardButton(text="/month_tasks")],
            [KeyboardButton(text="/quick_task"), KeyboardButton(text="/not_done")]
        ], resize_keyboard=True, persistent=True)

def payment_keyboard(lang: str = 'ru'):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Monobank (Украина)", url=MONOBANK_URL)],
        [InlineKeyboardButton(text=f"⭐ Telegram Stars ({STAR_PRICE} Stars)", callback_data="pay_stars")]
    ])
    return kb

# ==============================
# ХЕНДЛЕРЫ
# ==============================
@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    create_user(user_id, message.from_user.username or "", message.from_user.first_name or "Friend")

    lang = get_user_language(user_id)
    if lang != 'en':
        await send_main_welcome(message, lang, message.from_user.first_name)
        return

    # Выбор языка на английском
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=name, callback_data=f"set_lang_{code}")]
        for code, name in LANGUAGES.items()
    ])
    await message.answer(TRANSLATIONS['en']['start_hello'], parse_mode="Markdown", reply_markup=kb)
    await asyncio.sleep(1.5)
    await message.answer(TRANSLATIONS['en']['enable_notifications'])

@dp.callback_query(F.data.startswith("set_lang_"))
async def set_language(callback: CallbackQuery):
    lang = callback.data.split("_")[-1]
    update_user_language(callback.from_user.id, lang)
    await callback.message.edit_text(f"✅ {LANGUAGES.get(lang, lang)}")
    await send_main_welcome(callback.message, lang, callback.from_user.first_name)
    await callback.answer()

async def send_main_welcome(message: Message, lang: str, name="друг"):
    t = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    text = t['main_welcome'] + "\n\n" + t.get('trial_info', "")
    await message.answer(text, parse_mode="Markdown", reply_markup=main_menu_keyboard(lang))
    
    await asyncio.sleep(1)
    await message.answer(t.get('payment_title', "Choose payment method:"), 
                        reply_markup=payment_keyboard(lang))

# ==================== ОПЛАТА ====================
@dp.callback_query(F.data == "pay_stars")
async def pay_with_stars(callback: CallbackQuery):
    await callback.answer()
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Подписка Mikky Bot",
        description="Полный доступ на 30 дней",
        payload=f"subscription_{callback.from_user.id}",
        provider_token="",
        currency="XTR",
        prices=[types.LabeledPrice(label="1 месяц", amount=STAR_PRICE)]
    )

@dp.pre_checkout_query()
async def pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@dp.message(F.successful_payment)
async def successful_payment(message: Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("mikky.db")
    c = conn.cursor()
    c.execute("UPDATE users SET is_paid=1, trial_start=NULL WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
    
    lang = get_user_language(user_id)
    await message.answer("✅ Оплата прошла успешно!\nПодписка активирована на 30 дней 🌟", 
                        reply_markup=main_menu_keyboard(lang))

# ==================== КОМАНДЫ МЕНЮ ====================
@dp.message(Command(["новая_задача", "new_task"]))
async def new_task_cmd(message: Message):
    await message.answer("✅ Напиши новую задачу (можно с датой и временем):")

@dp.message(Command(["мои_задачи_на_день", "today_tasks"]))
async def today_tasks_cmd(message: Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    tasks = get_tasks_for_today(user_id)
    text = "📅 **Задачи на сегодня:**\n\n" if lang == 'ru' else "**Today's tasks:**\n\n"
    if not tasks:
        text += "Задач нет 🎉" if lang == 'ru' else "No tasks 🎉"
    else:
        for task_text, task_time in tasks:
            time_str = f"({task_time}) " if task_time else ""
            text += f"• {time_str}{task_text}\n"
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command(["мои_задачи_на_неделю", "week_tasks"]))
async def week_tasks_cmd(message: Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    tasks = get_tasks_for_week(user_id)
    text = "📅 **Задачи на неделю:**\n\n" if lang == 'ru' else "**Weekly tasks:**\n\n"
    if not tasks:
        text += "Задач нет." if lang == 'ru' else "No tasks."
    else:
        for task_text, date, time in tasks:
            text += f"• {date} {time or ''} — {task_text}\n"
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command(["мои_задачи_на_месяц", "month_tasks"]))
async def month_tasks_cmd(message: Message):
    await week_tasks_cmd(message)

# ==================== РАССЫЛКА ====================
async def send_daily_plan():
    for user_id, first_name, lang in get_all_active_users():
        tasks = get_tasks_for_today(user_id)
        motivation = get_unique_message(user_id)
        task_str = "\n".join([f"• {t[0]}" for t in tasks]) or ("Нет задач" if lang == 'ru' else "No tasks")
        text = TRANSLATIONS.get(lang, TRANSLATIONS['en'])['daily_greeting'].format(
            name=first_name, tasks=task_str, motivation=motivation
        )
        try:
            await bot.send_message(user_id, text, parse_mode="Markdown")
        except:
            pass

# ==============================
# ЗАПУСК
# ==============================
async def main():
    init_db()
    scheduler.add_job(send_daily_plan, 'cron', hour=7, minute=0)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
