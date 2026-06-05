import asyncio
import logging
import sqlite3
import random
from datetime import datetime, timedelta
import pytz

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ============================================================
# НАСТРОЙКИ — ЗАПОЛНИ ЗДЕСЬ
# ============================================================
BOT_TOKEN = "8988206711:AAGmjkJ0t-hz0iU1cDmIgsXK9sXvxk6xJzg"
ADMIN_ID = 0  # ← ЗАМЕНИ на свой Telegram ID (узнай у @userinfobot)
MONOBANK_LINK = "https://send.monobank.ua/XXXXX"  # ← ЗАМЕНИ на свою ссылку
PRICE_UAH = 50
TIMEZONE = "Europe/Kiev"
# ============================================================

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
scheduler = AsyncIOScheduler(timezone=TIMEZONE)
tz = pytz.timezone(TIMEZONE)

# ─────────────────────────────────────────
# ПОСЛАНИЯ (100 штук)
# ─────────────────────────────────────────
MESSAGES_LIST = [
    "Лучшее время начать — сейчас, а не завтра.",
    "Маленькие шаги каждый день приводят к большим результатам.",
    "Не жди идеального момента — действуй, имея то, что есть.",
    "Страх — это лишь сигнал, что ты на пороге чего-то важного.",
    "Одна попытка стоит больше, чем сто сожалений.",
    "Дорогу осилит идущий, даже если он идет медленно.",
    "Твои действия громче твоих слов.",
    "Сделай первый шаг, и путь появится сам.",
    "Не бойся ошибаться — бойся стоять на месте.",
    "Каждый новый день — это чистый лист. Напиши свою историю.",
    "Двигайся, даже если кажется, что нет сил.",
    "Начни с того, что есть, сделай то, что можешь.",
    "Лучше сделать и пожалеть, чем не сделать и жалеть всю жизнь.",
    "Возьми ответственность за свою жизнь в свои руки.",
    "Мысль без действия — всего лишь мечта.",
    "Ты способен на гораздо большее, чем думаешь.",
    "Никто не может заставить тебя чувствовать себя неполноценным без твоего согласия.",
    "Сравнивай себя только с собой вчерашним.",
    "Твоя ценность не зависит от мнения других людей.",
    "Ты — автор своей жизни, не будь просто читателем.",
    "Доверяй своему внутреннему голосу.",
    "У тебя есть всё необходимое, чтобы добиться успеха.",
    "Ты уникален, и в этом твоя сила.",
    "Перестань искать одобрения — найди себя.",
    "Верь в свою идею, даже если никто не верит.",
    "Твоё прошлое — не приговор. Это опыт.",
    "Ты уже пережил 100% своих плохих дней.",
    "Не уменьшай свою ценность, чтобы угодить другим.",
    "Прими свои недостатки — они делают тебя настоящим.",
    "Ты достоин счастья, успеха и любви.",
    "После дождя всегда приходит радуга.",
    "Падать не страшно — страшно не подниматься.",
    "Любая неудача — это урок, а не финал.",
    "Трудности делают тебя сильнее.",
    "Стена стоит только на пути тех, кто не хочет её обойти.",
    "Самые сильные люди рождаются из самых сложных ситуаций.",
    "Сдаться — это единственный способ проиграть.",
    "В конце каждой туннеля есть свет, просто нужно продолжать идти.",
    "Не проблема важна, а твоя реакция на неё.",
    "Разреши себе быть несовершенным, но настойчивым.",
    "Всё, что тебя не убивает, делает тебя мудрее.",
    "Твой предел — это только то, что ты сам себе установил.",
    "Вместо «Почему это случилось со мной?» спроси «Чему это меня учит?».",
    "Самая большая слава — не в том, чтобы никогда не падать, а в том, чтобы вставать каждый раз.",
    "Шторм заканчивается, и море снова становится спокойным.",
    "Капля камень точит не силой, а частотой падения.",
    "Дисциплина — это мост между целями и их достижением.",
    "Система важнее, чем мотивация.",
    "Делай сегодня то, что другие не хотят, чтобы завтра жить так, как другие не могут.",
    "Поставь цель и не отвлекайся на шум.",
    "1% улучшения каждый день = 3700% в год.",
    "Упорство побеждает талант, если талант не упорен.",
    "Сфокусируйся на процессе, результат придет сам.",
    "Легких путей к великим целям не бывает.",
    "Твоя зона комфорта — враг твоего роста.",
    "Иди к цели с упорством голодного волка.",
    "Каждый пропущенный день — это шаг назад.",
    "Сначала ты работаешь на свою репутацию, потом репутация работает на тебя.",
    "Не откладывай жизнь на потом — живи сейчас, достигай сейчас.",
    "Терпение — это не пассивность, это сила выдержки.",
    "Мир полон возможностей, нужно только открыть глаза.",
    "Твои мысли формируют твою реальность.",
    "Окружай себя теми, кто поднимает тебя вверх.",
    "Читай. Учись. Расти. Повторяй.",
    "Позитивное мышление притягивает позитивные события.",
    "Вдохновение — это гость, который не любит посещать ленивых.",
    "Знание — это сила, а применение знания — суперсила.",
    "Будь благодарен за то, что имеешь, пока стремишься к большему.",
    "Ты — это среднее из пяти людей, с которыми проводишь больше всего времени.",
    "Инвестируй в себя — это единственное вложение, которое всегда окупается.",
    "Креативность — это просто соединение вещей.",
    "Любопытство — двигатель прогресса.",
    "Будь тем изменением, которое хочешь видеть в мире.",
    "Учись видеть хорошее в каждом дне.",
    "Мечты сбываются, когда ты перестаешь просто мечтать и начинаешь делать.",
    "Отдавай миру больше, чем берёшь.",
    "Искренность — самая сильная валюта.",
    "Умение слушать — редкий дар. Используй его.",
    "Помощь другим — лучший способ помочь себе.",
    "Создавай связи, а не контакты.",
    "Делай добро, и оно к тебе вернётся.",
    "Цени людей, которые верят в тебя, когда ты сам в себя не веришь.",
    "Твой успех — это успех твоей команды.",
    "Прощение — это не слабость, это освобождение.",
    "Будь лидером, а не начальником.",
    "Слово может ранить, но может и вдохновить. Выбирай мудро.",
    "Вдохновляй своим примером.",
    "Поддерживай других на их пути, и твой путь станет легче.",
    "Не суди людей, пока не прошел милю в их ботинках.",
    "Каждый человек несёт свою историю — будь добр.",
    "Улыбка — это самый короткий путь между двумя людьми.",
    "Настоящая дружба проверяется в трудные времена.",
    "Люби себя достаточно, чтобы требовать уважения.",
    "Твоё время — самый ценный ресурс. Трать его мудро.",
    "Сегодняшний день больше не повторится. Сделай его значимым.",
    "Маленькие победы складываются в большой успех.",
    "Живи так, чтобы вспоминать с улыбкой.",
    "Ты сильнее, чем кажешься, и умнее, чем думаешь.",
    "Каждый шаг вперёд — это победа над вчерашним собой.",
]

# ─────────────────────────────────────────
# БАЗА ДАННЫХ
# ─────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("miky.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        is_paid INTEGER DEFAULT 0,
        paid_until TEXT,
        joined_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        text TEXT,
        event_date TEXT,
        event_time TEXT,
        reminded_morning INTEGER DEFAULT 0,
        reminded_30min INTEGER DEFAULT 0,
        created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS sent_quotes (
        user_id INTEGER,
        quote_index INTEGER
    )""")
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect("miky.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def is_paid(user_id):
    if user_id == ADMIN_ID:
        return True
    user = get_user(user_id)
    if not user:
        return False
    if user[3] == 1:
        paid_until = user[4]
        if paid_until:
            now = datetime.now(tz).strftime("%Y-%m-%d")
            return paid_until >= now
    return False

def register_user(user_id, username, first_name):
    conn = sqlite3.connect("miky.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, joined_at) VALUES (?,?,?,?)",
              (user_id, username, first_name, datetime.now(tz).isoformat()))
    conn.commit()
    conn.close()

def activate_user(user_id):
    paid_until = (datetime.now(tz) + timedelta(days=30)).strftime("%Y-%m-%d")
    conn = sqlite3.connect("miky.db")
    c = conn.cursor()
    c.execute("UPDATE users SET is_paid=1, paid_until=? WHERE user_id=?", (paid_until, user_id))
    conn.commit()
    conn.close()
    return paid_until

def get_random_quote(user_id):
    conn = sqlite3.connect("miky.db")
    c = conn.cursor()
    c.execute("SELECT quote_index FROM sent_quotes WHERE user_id=?", (user_id,))
    used = [r[0] for r in c.fetchall()]
    available = [i for i in range(len(MESSAGES_LIST)) if i not in used]
    if not available:
        c.execute("DELETE FROM sent_quotes WHERE user_id=?", (user_id,))
        conn.commit()
        available = list(range(len(MESSAGES_LIST)))
    idx = random.choice(available)
    c.execute("INSERT INTO sent_quotes VALUES (?,?)", (user_id, idx))
    conn.commit()
    conn.close()
    return MESSAGES_LIST[idx]

def save_event(user_id, text, event_date=None, event_time=None):
    conn = sqlite3.connect("miky.db")
    c = conn.cursor()
    c.execute("INSERT INTO events (user_id, text, event_date, event_time, created_at) VALUES (?,?,?,?,?)",
              (user_id, text, event_date, event_time, datetime.now(tz).isoformat()))
    conn.commit()
    conn.close()

def get_week_events(user_id):
    conn = sqlite3.connect("miky.db")
    c = conn.cursor()
    today = datetime.now(tz).date()
    week_end = today + timedelta(days=7)
    c.execute("SELECT text, event_date, event_time FROM events WHERE user_id=? AND event_date BETWEEN ? AND ? ORDER BY event_date, event_time",
              (user_id, today.strftime("%Y-%m-%d"), week_end.strftime("%Y-%m-%d")))
    rows = c.fetchall()
    conn.close()
    return rows

def get_today_events(user_id):
    conn = sqlite3.connect("miky.db")
    c = conn.cursor()
    today = datetime.now(tz).strftime("%Y-%m-%d")
    c.execute("SELECT id, text, event_time FROM events WHERE user_id=? AND event_date=? ORDER BY event_time",
              (user_id, today))
    rows = c.fetchall()
    conn.close()
    return rows

def get_all_paid_users():
    conn = sqlite3.connect("miky.db")
    c = conn.cursor()
    today = datetime.now(tz).strftime("%Y-%m-%d")
    c.execute("SELECT user_id, username, first_name FROM users WHERE is_paid=1 AND paid_until>=?", (today,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_all_users():
    conn = sqlite3.connect("miky.db")
    c = conn.cursor()
    c.execute("SELECT user_id, username, first_name, is_paid, paid_until FROM users")
    rows = c.fetchall()
    conn.close()
    return rows

# ─────────────────────────────────────────
# ХЕНДЛЕРЫ
# ─────────────────────────────────────────
@dp.message(Command("start"))
async def cmd_start(msg: Message):
    register_user(msg.from_user.id, msg.from_user.username, msg.from_user.first_name)
    name = msg.from_user.first_name or msg.from_user.username or "друг"
    await msg.answer(
        f"👋 Привет, {name}!\n\n"
        f"Я твой новый помощник *Mikky* 🐕\n\n"
        f"Расскажи мне о своих планах! Просто напиши что-нибудь вроде:\n"
        f"• «Завтра кофе с Леной в 15:00»\n"
        f"• «В пятницу встреча в 10:00»\n"
        f"• Или просто перешли ссылку / фото с заметкой\n\n"
        f"Я запомню и напомню тебе вовремя 🗓️\n\n"
        f"📌 Команды:\n"
        f"/plans — мои планы на неделю\n"
        f"/today — задачи на сегодня\n"
        f"/pay — оплатить доступ (50 грн/мес)\n"
        f"/help — помощь",
        parse_mode="Markdown"
    )

@dp.message(Command("pay"))
async def cmd_pay(msg: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить 50 грн", url=MONOBANK_LINK)],
        [InlineKeyboardButton(text="✅ Я оплатил(а)", callback_data=f"paid_{msg.from_user.id}")]
    ])
    await msg.answer(
        "💰 *Доступ к Mikky Helper*\n\n"
        "Стоимость: *50 грн / месяц*\n\n"
        "1️⃣ Нажми кнопку «Оплатить 50 грн»\n"
        "2️⃣ После оплаты нажми «Я оплатил(а)»\n"
        "3️⃣ Администратор подтвердит доступ\n\n"
        "После активации ты получишь:\n"
        "✅ Сохранение планов и напоминаний\n"
        "✅ Утренние сводки задач\n"
        "✅ Напоминание за 30 мин до события\n"
        "✅ План на неделю каждое воскресенье\n"
        "✅ Ежедневное мотивационное послание",
        parse_mode="Markdown",
        reply_markup=kb
    )

@dp.callback_query(F.data.startswith("paid_"))
async def cb_paid(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    user = get_user(user_id)
    name = user[2] if user else "Пользователь"
    username = f"@{user[1]}" if user and user[1] else str(user_id)

    # Уведомляем админа
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Активировать", callback_data=f"activate_{user_id}")],
        [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{user_id}")]
    ])
    await bot.send_message(
        ADMIN_ID,
        f"💰 *Новый запрос на оплату!*\n\n"
        f"👤 {name} ({username})\n"
        f"ID: `{user_id}`\n"
        f"Сумма: 50 грн",
        parse_mode="Markdown",
        reply_markup=kb
    )
    await callback.message.answer(
        "✅ Твой запрос отправлен администратору!\n"
        "Доступ будет активирован после проверки оплаты (обычно в течение нескольких часов)."
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("activate_"))
async def cb_activate(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа")
        return
    user_id = int(callback.data.split("_")[1])
    paid_until = activate_user(user_id)
    await bot.send_message(
        user_id,
        f"🎉 *Доступ активирован!*\n\n"
        f"Подписка действует до: *{paid_until}*\n\n"
        f"Теперь просто пиши мне о своих планах, и я всё запомню! 🐕",
        parse_mode="Markdown"
    )
    await callback.message.edit_text(f"✅ Пользователь {user_id} активирован до {paid_until}")
    await callback.answer()

@dp.callback_query(F.data.startswith("reject_"))
async def cb_reject(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа")
        return
    user_id = int(callback.data.split("_")[1])
    await bot.send_message(
        user_id,
        "❌ К сожалению, оплата не подтверждена.\n"
        "Если это ошибка — напиши нам."
    )
    await callback.message.edit_text(f"❌ Пользователь {user_id} отклонён")
    await callback.answer()

@dp.message(Command("plans"))
async def cmd_plans(msg: Message):
    if not is_paid(msg.from_user.id):
        await msg.answer("🔒 Эта функция доступна только после оплаты.\nНапиши /pay чтобы получить доступ.")
        return
    events = get_week_events(msg.from_user.id)
    if not events:
        await msg.answer("📭 У тебя нет планов на ближайшую неделю.\n\nПросто напиши мне о своих делах!")
        return
    text = "📅 *Твои планы на неделю:*\n\n"
    for ev in events:
        t = f" в {ev[2]}" if ev[2] else ""
        d = ev[1] if ev[1] else "дата не указана"
        text += f"• {ev[0]} — {d}{t}\n"
    await msg.answer(text, parse_mode="Markdown")

@dp.message(Command("today"))
async def cmd_today(msg: Message):
    if not is_paid(msg.from_user.id):
        await msg.answer("🔒 Эта функция доступна только после оплаты.\nНапиши /pay чтобы получить доступ.")
        return
    await send_morning_summary(msg.from_user.id, msg.from_user.first_name)

@dp.message(Command("help"))
async def cmd_help(msg: Message):
    await msg.answer(
        "🐕 *Mikky Helper — помощник по планам*\n\n"
        "Просто напиши мне о своих планах:\n"
        "• «Завтра кофе с Леной в 15:00»\n"
        "• «В пятницу встреча в 10:00»\n"
        "• «12 июня врач в 11:30»\n\n"
        "Я пойму дату и время и напомню тебе!\n\n"
        "📌 *Команды:*\n"
        "/plans — планы на неделю\n"
        "/today — задачи на сегодня\n"
        "/pay — оплатить доступ\n\n"
        "📩 Вопросы? Просто напиши сюда.",
        parse_mode="Markdown"
    )

# Админ-команды
@dp.message(Command("admin"))
async def cmd_admin(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return
    users = get_all_users()
    paid = sum(1 for u in users if u[3] == 1)
    text = f"👑 *Панель администратора*\n\n"
    text += f"Всего пользователей: {len(users)}\n"
    text += f"Активных подписок: {paid}\n\n"
    for u in users[-20:]:
        status = "✅" if u[3] == 1 else "🔒"
        uname = f"@{u[1]}" if u[1] else str(u[0])
        text += f"{status} {u[2]} ({uname}) до {u[4] or '—'}\n"
    await msg.answer(text, parse_mode="Markdown")

# Обработка любого сообщения (сохранение планов)
@dp.message()
async def handle_any(msg: Message):
    if not is_paid(msg.from_user.id):
        name = msg.from_user.first_name or "друг"
        await msg.answer(
            f"👋 {name}, чтобы я мог запоминать твои планы, нужна подписка.\n\n"
            f"💰 Всего *50 грн/месяц* — нажми /pay",
            parse_mode="Markdown"
        )
        return

    # Парсим дату/время из текста с помощью простых правил
    text = msg.text or msg.caption or "[медиафайл]"
    event_date, event_time = parse_datetime(text)
    save_event(msg.from_user.id, text, event_date, event_time)

    reply = "✅ Записала! "
    if event_date:
        reply += f"Дата: {event_date}"
        if event_time:
            reply += f" в {event_time}"
        reply += "\nНапомню тебе утром и за 30 мин до события 🔔"
    else:
        reply += "Сохранила в заметки (дату не нашла — уточни если нужно напоминание)"

    await msg.answer(reply)

# ─────────────────────────────────────────
# ПАРСИНГ ДАТЫ/ВРЕМЕНИ
# ─────────────────────────────────────────
def parse_datetime(text):
    import re
    text_lower = text.lower()
    today = datetime.now(tz).date()

    event_date = None
    event_time = None

    # Время: HH:MM
    time_match = re.search(r'\b(\d{1,2})[:\.](\d{2})\b', text)
    if time_match:
        h, m = int(time_match.group(1)), int(time_match.group(2))
        if 0 <= h <= 23 and 0 <= m <= 59:
            event_time = f"{h:02d}:{m:02d}"

    # Слова-дни
    if "сегодня" in text_lower:
        event_date = today.strftime("%Y-%m-%d")
    elif "завтра" in text_lower:
        event_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    elif "послезавтра" in text_lower:
        event_date = (today + timedelta(days=2)).strftime("%Y-%m-%d")

    # Дни недели
    days_map = {
        "понедельник": 0, "вторник": 1, "среда": 2, "среду": 2,
        "четверг": 3, "пятница": 4, "пятницу": 4, "суббота": 5,
        "субботу": 5, "воскресенье": 6
    }
    if not event_date:
        for day_name, day_num in days_map.items():
            if day_name in text_lower:
                diff = (day_num - today.weekday()) % 7
                if diff == 0:
                    diff = 7
                event_date = (today + timedelta(days=diff)).strftime("%Y-%m-%d")
                break

    # Формат: DD.MM или DD июня и т.д.
    if not event_date:
        months = {"января":1,"февраля":2,"марта":3,"апреля":4,"мая":5,"июня":6,
                  "июля":7,"августа":8,"сентября":9,"октября":10,"ноября":11,"декабря":12}
        m = re.search(r'(\d{1,2})\s+(' + '|'.join(months.keys()) + r')', text_lower)
        if m:
            day = int(m.group(1))
            month = months[m.group(2)]
            year = today.year
            try:
                d = datetime(year, month, day).date()
                if d < today:
                    d = datetime(year+1, month, day).date()
                event_date = d.strftime("%Y-%m-%d")
            except:
                pass

    return event_date, event_time

# ─────────────────────────────────────────
# ПЛАНИРОВЩИК УВЕДОМЛЕНИЙ
# ─────────────────────────────────────────
async def send_morning_summary(user_id, first_name=None):
    events = get_today_events(user_id)
    user = get_user(user_id)
    name = first_name or (user[2] if user else "")
    quote = get_random_quote(user_id)

    if not events:
        text = (
            f"🌅 Доброе утро, *{name}*!\n\n"
            f"📭 На сегодня планов нет — свободный день!\n\n"
            f"💫 *Послание дня:*\n_{quote}_"
        )
    else:
        task_list = ""
        for ev in events:
            t = f" в {ev[2]}" if ev[2] else ""
            task_list += f"• {ev[1]}{t}\n"
        text = (
            f"🌅 Доброе утро, *{name}*!\n\n"
            f"📋 Твои задачи на сегодня:\n\n"
            f"{task_list}\n"
            f"💫 *Послание дня:*\n_{quote}_"
        )
    await bot.send_message(user_id, text, parse_mode="Markdown")

async def morning_job():
    users = get_all_paid_users()
    for user in users:
        try:
            await send_morning_summary(user[0], user[2])
        except Exception as e:
            logging.error(f"Morning job error for {user[0]}: {e}")

async def reminder_30min_job():
    conn = sqlite3.connect("miky.db")
    c = conn.cursor()
    now = datetime.now(tz)
    target_time = (now + timedelta(minutes=30)).strftime("%H:%M")
    today = now.strftime("%Y-%m-%d")
    c.execute("""SELECT id, user_id, text, event_time FROM events 
                 WHERE event_date=? AND event_time=? AND reminded_30min=0""",
              (today, target_time))
    rows = c.fetchall()
    for row in rows:
        event_id, user_id, text, event_time = row
        if is_paid(user_id):
            try:
                await bot.send_message(
                    user_id,
                    f"⏰ *Напоминание!*\n\nЧерез 30 минут ({event_time}):\n_{text}_",
                    parse_mode="Markdown"
                )
                c.execute("UPDATE events SET reminded_30min=1 WHERE id=?", (event_id,))
            except Exception as e:
                logging.error(f"Reminder error: {e}")
    conn.commit()
    conn.close()

async def weekly_plan_job():
    users = get_all_paid_users()
    for user in users:
        try:
            user_id, username, first_name = user
            events = get_week_events(user_id)
            name = first_name or username or "друг"

            if not events:
                text = (
                    f"📅 *{name}, план на следующую неделю:*\n\n"
                    f"📭 Пока планов нет.\n"
                    f"Напиши мне о своих делах, и я всё запомню!"
                )
            else:
                task_list = ""
                for ev in events:
                    t = f" в {ev[2]}" if ev[2] else ""
                    d = ev[1] or "дата не указана"
                    task_list += f"• {ev[0]} — {d}{t}\n"
                text = (
                    f"📅 *{name}, твой план на неделю:*\n\n"
                    f"{task_list}\n"
                    f"Хорошей недели! 🐕"
                )
            await bot.send_message(user_id, text, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Weekly plan error for {user[0]}: {e}")

# ─────────────────────────────────────────
# ЗАПУСК
# ─────────────────────────────────────────
async def main():
    init_db()

    # Утреннее сообщение каждый день в 8:00
    scheduler.add_job(morning_job, "cron", hour=8, minute=0)

    # Проверка напоминаний каждую минуту
    scheduler.add_job(reminder_30min_job, "interval", minutes=1)

    # Воскресенье в 17:00 — план на неделю
    scheduler.add_job(weekly_plan_job, "cron", day_of_week="sun", hour=17, minute=0)

    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
