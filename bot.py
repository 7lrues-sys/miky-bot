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
STAR_PRICE = 300
MONOBANK_URL = "https://send.monobank.ua/jar/5gfL2BGRr3"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler(timezone=TIMEZONE)

# ==============================
# ЯЗЫКИ
# ==============================
LANGUAGES = {
    'en': '🇬🇧 English',
    'uk': '🇺🇦 Українська',
    'ru': '🇷🇺 Русский',
    'zh': '🇨🇳 中文 (普通话)', 'hi': '🇮🇳 हिन्दी',
    'es': '🇪🇸 Español', 'fr': '🇫🇷 Français', 'ar': '🇸🇦 العربية',
    'bn': '🇧🇩 বাংলা', 'pt': '🇧🇷 Português',
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
        'main_welcome': "Hello! I am your new assistant *Mikky* 🌟\n\nTell me about your plans!\n\nJust send:\n• Text notes\n• Photos\n• Links\n• Task with time (Tomorrow coffee Lena 15:00)",
        'trial_info': "You have 7 days of free access.\nAfter trial — subscription.",
        'payment_title': "Choose payment method:",
        'daily_greeting': "🌅 Good morning, {name}!\n\n**Today's plan:**\n{tasks}\n\n💡 {motivation}"
    },
    'ru': {
        'start_hello': "🌟 Привет! Я твой новый помощник *Mikky*! 🌟\n\nВыбери язык:",
        'main_welcome': "Привет! Я твой новый помощник *Mikky* 🌟\n\nРасскажи мне о своих планах!\n\nПросто пиши:\n• 📝 Текстовые заметки\n• 📸 Фото\n• 🔗 Ссылки\n• Задачи с временем (Завтра кофе Лена 15:00)",
        'trial_info': "У тебя есть 7 дней бесплатного доступа.\nПосле триала — подписка 99 UAH.",
        'payment_title': "Выбери способ оплаты:",
        'daily_greeting': "🌅 Доброе утро, {name}!\n\n**План на сегодня:**\n{tasks}\n\n💡 {motivation}"
    },
    'uk': {
        'start_hello': "🌟 Привіт! Я твій новий помічник *Mikky*! 🌟\n\nОбери мову:",
        'main_welcome': "Привіт! Я твій новий помічник *Mikky* 🌟\n\nРозкажи мені про свої плани!\n\nПросто пиши:\n• 📝 Текстові нотатки\n• 📸 Фото\n• 🔗 Посилання\n• Задачі з часом (Завтра кава Лена 15:00)",
        'trial_info': "У тебе є 7 днів безкоштовного доступу.\nПісля тріалу — підписка 99 UAH.",
        'payment_title': "Обери спосіб оплати:",
        'daily_greeting': "🌅 Доброго ранку, {name}!\n\n**План на сьогодні:**\n{tasks}\n\n💡 {motivation}"
    }
}

# ==============================
# МОТИВАЦИЯ
# ==============================
MESSAGES = [
    "Ты способна на всё, что задумаешь 💫",
    "Каждый день — новый шанс стать лучше 🌱",
    "Всё в твоей жизни складывается правильно 🧩"
]

# ==============================
# БАЗА ДАННЫХ
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
    if lang == 'uk':
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="➕ Нова задача"), KeyboardButton(text="📅 На сьогодні")],
            [KeyboardButton(text="📅 На тиждень"), KeyboardButton(text="📅 На місяць")],
            [KeyboardButton(text="⚡ Швидко зробити"), KeyboardButton(text="❓ Не зроблено")]
        ], resize_keyboard=True, persistent=True)
    elif lang == 'ru':
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="➕ Новая задача"), KeyboardButton(text="📅 На сегодня")],
            [KeyboardButton(text="📅 На неделю"), KeyboardButton(text="📅 На месяц")],
            [KeyboardButton(text="⚡ Быстро сделать"), KeyboardButton(text="❓ Не сделано")]
        ], resize_keyboard=True, persistent=True)
    else:
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="➕ New Task"), KeyboardButton(text="📅 Today")],
            [KeyboardButton(text="📅 Week"), KeyboardButton(text="📅 Month")],
            [KeyboardButton(text="⚡ Quick Task"), KeyboardButton(text="❓ Not Done")]
        ], resize_keyboard=True, persistent=True)

def payment_keyboard(lang: str = 'ru'):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Monobank", url=MONOBANK_URL)],
        [InlineKeyboardButton(text=f"⭐ Telegram Stars ({STAR_PRICE})", callback_data="pay_stars")]
    ])

# ==============================
# ХЕНДЛЕРЫ
# ==============================
@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    create_user(user_id, message.from_user.username or "", message.from_user.first_name or "Друг")

    lang = get_user_language(user_id)
    if lang != 'en':
        await send_main_welcome(message, lang, message.from_user.first_name)
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=name, callback_data=f"set_lang_{code}")]
        for code, name in LANGUAGES.items()
    ])
    await message.answer(TRANSLATIONS['en']['start_hello'], parse_mode="Markdown", reply_markup=kb)

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
    
    await asyncio.sleep(1.2)
    
    notif = {
        'ru': "🔔 Будь ласка, увімкни сповіщення!\n1. Натисни на назву бота зверху\n2. Натисни ⋮\n3. Обери «Сповіщення» → Увімкни",
        'uk': "🔔 Будь ласка, увімкни сповіщення від бота!\n1. Натисни на назву бота зверху\n2. Натисни ⋮\n3. Обери «Сповіщення» → Увімкни",
        'en': "🔔 Please enable notifications!\n1. Tap bot name at the top\n2. Tap ⋮\n3. Select Notifications → ON"
    }.get(lang, "🔔 Enable notifications!")
    
    await message.answer(notif)
    
    await asyncio.sleep(0.8)
    await message.answer(t.get('payment_title', "Choose payment:"), reply_markup=payment_keyboard(lang))

# Оплата и другие хендлеры (оставил основные)
@dp.callback_query(F.data == "pay_stars")
async def pay_with_stars(callback: CallbackQuery):
    await callback.answer()
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Підписка Mikky Bot",
        description="Повний доступ на 30 днів",
        payload=f"subscription_{callback.from_user.id}",
        provider_token="",
        currency="XTR",
        prices=[types.LabeledPrice(label="1 місяць", amount=STAR_PRICE)]
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
    await message.answer("✅ Оплата пройшла успішно! Підписка активована 🌟", reply_markup=main_menu_keyboard(lang))

# Команды меню
@dp.message(Command(commands=["нова_задача", "новая_задача", "new_task"]))
@dp.message(F.text.contains("Нова задача") | F.text.contains("Новая задача") | F.text.contains("New Task"))
async def new_task_cmd(message: Message):
    await message.answer("✅ Напиши нову задачу (можна з датою та часом):")

# ... (другие команды можно добавить аналогично)

# Ежедневная рассылка
async def send_daily_plan():
    for user_id, first_name, lang in get_all_active_users():
        tasks = get_tasks_for_today(user_id)
        motivation = get_unique_message(user_id)
        task_str = "\n".join([f"• {t[0]}" for t in tasks]) or "Немає задач"
        text = TRANSLATIONS.get(lang, TRANSLATIONS['en'])['daily_greeting'].format(
            name=first_name, tasks=task_str, motivation=motivation
        )
        try:
            await bot.send_message(user_id, text, parse_mode="Markdown")
        except:
            pass

async def main():
    init_db()
    scheduler.add_job(send_daily_plan, 'cron', hour=7, minute=0)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
