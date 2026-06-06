import asyncio
import logging
import sqlite3
import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz

# ==============================
# НАСТРОЙКИ
# ==============================
BOT_TOKEN = "8988206711:AAGmjkJ0t-hz0iU1cDmIgsXK9sXvxk6xJzg"
SUBSCRIPTION_PRICE = 99  # UAH
TIMEZONE = pytz.timezone("Europe/Kiev")
TRIAL_DAYS = 7

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler(timezone=TIMEZONE)

# ==============================
# ПОСЛАНИЯ (100 штук)
# ==============================
MESSAGES = [
    "Ты способна на всё, что задумаешь 💫",
    "Каждый день — новый шанс стать лучше 🌱",
    "Твои мечты заслуживают действий 🚀",
    "Верь в себя — ты уже на правильном пути ✨",
    "Маленькие шаги ведут к большим победам 🏆",
    "Сегодня отличный день для новых начинаний 🌅",
    "Ты сильнее, чем думаешь 💪",
    "Твоя энергия заразительна — дари её миру 🌟",
    "Не сравнивай себя с другими — у тебя свой путь 🌈",
    "Радость живёт в маленьких моментах 🎈",
    "Ты заслуживаешь всего самого лучшего 👑",
    "Сделай один шаг — остальное придёт 🦋",
    "Твои идеи важны и нужны этому миру 💡",
    "Сегодня сделай что-то только для себя ❤️",
    "Трудности делают тебя мудрее 🌊",
    "Ты уже многого добилась — гордись собой 🎯",
    "Улыбнись — это меняет всё 😊",
    "Позволь себе отдыхать — это тоже продуктивность 🍃",
    "Твоя интуиция — лучший советник 🔮",
    "Каждая ошибка — урок на пути к успеху 📚",
    "Ты создаёшь свою реальность мыслями и действиями 🌍",
    "Будь добра к себе так же, как к близким 🤍",
    "Сегодняшние усилия — завтрашние результаты ⚡",
    "Твоя уникальность — твоя суперсила 🦸‍♀️",
    "Позволь себе мечтать по-крупному 🌙",
    "Ты меняешь мир вокруг себя к лучшему 🌸",
    "Всё получится — просто продолжай идти 🛤️",
    "Ты достаточно хороша прямо сейчас 💝",
    "Каждый день — подарок, используй его мудро 🎁",
    "Твоя настойчивость вдохновляет 🔥",
    "Доверяй процессу — результат придёт 🌿",
    "Ты окружена людьми, которые тебя любят 🫶",
    "Твой успех неизбежен 🏅",
    "Наслаждайся путём, не только целью 🗺️",
    "Сила внутри тебя — безгранична ⚡",
    "Ты вдохновляешь других своим примером 🌺",
    "Хорошие дела возвращаются сторицей 🔄",
    "Твоё время ценно — трать его на важное ⏰",
    "Смелость — это не отсутствие страха, а действие вопреки ему 🦁",
    "Ты заслуживаешь любви и уважения 💖",
    "Каждое утро — чистый лист 📝",
    "Ты можешь больше, чем себе позволяешь 🚀",
    "Твоя улыбка освещает всё вокруг ☀️",
    "Верь — и мир откликнется 🌠",
    "Ты на верном пути, даже когда сомневаешься 🧭",
    "Твои таланты уникальны и ценны 🎨",
    "Будь собой — это лучшее, что ты можешь делать 💎",
    "Сегодня ты ближе к цели, чем вчера 📈",
    "Твоя история ещё пишется — и она прекрасна ✍️",
    "Делай с любовью — и всё будет хорошо 💓",
    "Ты справишься — ты всегда справляешься 🌟",
    "Позволь себе быть несовершенной — это нормально 🌼",
    "Твои границы — это твоя сила 🛡️",
    "Каждый момент имеет значение 🕊️",
    "Ты создана для великих вещей 👸",
    "Доверяй себе больше 🔑",
    "Твоё спокойствие — твоя власть 🌊",
    "Радость — твой естественный state 🎶",
    "Ты заслуживаешь отдыха без чувства вины 🛁",
    "Твои планы важны — и ты важна 🌹",
    "Всё, что ты делаешь — имеет смысл 🎯",
    "Ты богаче, чем думаешь — опытом, любовью, мудростью 💰",
    "Сегодня — идеальный день для маленьких побед 🏆",
    "Твоя забота о себе — это инвестиция 💅",
    "Каждая задача, которую ты ставишь — выполнима 📌",
    "Ты умеешь находить выход из любой ситуации 🗝️",
    "Твоя интуиция никогда тебя не подводила 🔮",
    "Позволь хорошему случиться 🍀",
    "Твои усилия видны — даже когда кажется иначе 👀",
    "Ты меняешься к лучшему каждый день 🌱",
    "Всё в твоей жизни складывается правильно 🧩",
    "Ты заслуживаешь того, о чём мечтаешь 💭",
    "Твоё «нет» так же важно, как «да» 🚦",
    "Ты — автор своей жизни ✒️",
    "Сегодня сделай что-то, что тебя радует 🎠",
    "Ты не одна — у тебя есть поддержка 🤝",
    "Твои мысли формируют реальность — выбирай лучшие 💬",
    "Ты уже победила, встав и начав день 🌤️",
    "Настоящий момент — лучший момент 🕰️",
    "Твои чувства важны и заслуживают внимания 💙",
    "Ты справляешься лучше, чем думаешь 🌟",
    "Маленький прогресс — это всё равно прогресс 📊",
    "Ты достойна всего хорошего без условий 🎀",
    "Позволь себе сиять ✨",
    "Твоя жизнь — произведение искусства 🖼️",
    "Каждая задача начинается с первого шага 👣",
    "Ты умная, смелая и красивая 🌸",
    "Твоя работа над собой заметна 🪞",
    "Сегодня хороший день быть живой 🌍",
    "Ты привлекаешь то, что излучаешь — излучай добро ☀️",
    "Твоя цель уже ждёт тебя 🎯",
    "Всё, что ты делаешь — важно 💼",
    "Ты — источник вдохновения для тех, кто рядом 🕯️",
    "Твои мечты реальны — действуй 🌟",
    "Сегодня и каждый день — ты достаточна 💗",
    "Жизнь любит тебя — открой ей сердце 💞",
    "Ты создана для радости и процветания 🌺",
    "Верь в себя — это самое важное 🙌",
]

# ==============================
# БАЗА ДАННЫХ
# ==============================
def init_db():
    conn = sqlite3.connect("mikky.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            is_paid INTEGER DEFAULT 0,
            used_messages TEXT DEFAULT '',
            trial_start TEXT DEFAULT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            text TEXT,
            event_date TEXT,
            event_time TEXT,
            notified_morning INTEGER DEFAULT 0,
            notified_30min INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect("mikky.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def create_user(user_id, username, first_name):
    conn = sqlite3.connect("mikky.db")
    c = conn.cursor()
    trial_start = datetime.now(TIMEZONE).isoformat()
    c.execute(
        "INSERT OR IGNORE INTO users (user_id, username, first_name, trial_start) VALUES (?,?,?,?)",
        (user_id, username, first_name, trial_start)
    )
    conn.commit()
    conn.close()

def has_access(user_id):
    """Проверяет: оплачено ИЛИ триал ещё активен"""
    user = get_user(user_id)
    if not user:
        return False
    is_paid_flag = user[3] == 1
    if is_paid_flag:
        return True
    # Проверка триала (колонка 5 = trial_start)
    trial_start = user[5] if len(user) > 5 else None
    if trial_start:
        start_dt = datetime.fromisoformat(trial_start)
        if start_dt.tzinfo is None:
            start_dt = TIMEZONE.localize(start_dt)
        now = datetime.now(TIMEZONE)
        if (now - start_dt).days < TRIAL_DAYS:
            return True
    return False

def trial_days_left(user_id):
    user = get_user(user_id)
    if not user or len(user) <= 5 or not user[5]:
        return 0
    start_dt = datetime.fromisoformat(user[5])
    if start_dt.tzinfo is None:
        start_dt = TIMEZONE.localize(start_dt)
    elapsed = (datetime.now(TIMEZONE) - start_dt).days
    return max(0, TRIAL_DAYS - elapsed)

def set_paid(user_id):
    conn = sqlite3.connect("mikky.db")
    c = conn.cursor()
    c.execute("UPDATE users SET is_paid=1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def save_task(user_id, text, event_date=None, event_time=None):
    conn = sqlite3.connect("mikky.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO tasks (user_id, text, event_date, event_time, created_at)
        VALUES (?,?,?,?,?)
    """, (user_id, text, event_date, event_time, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_tasks_for_week(user_id):
    now = datetime.now(TIMEZONE)
    week_end = now + timedelta(days=7)
    conn = sqlite3.connect("mikky.db")
    c = conn.cursor()
    c.execute("""
        SELECT text, event_date, event_time FROM tasks
        WHERE user_id=? AND event_date >= ? AND event_date <= ?
        ORDER BY event_date, event_time
    """, (user_id, now.strftime("%Y-%m-%d"), week_end.strftime("%Y-%m-%d")))
    rows = c.fetchall()
    conn.close()
    return rows

def get_tasks_for_today(user_id):
    today = datetime.now(TIMEZONE).strftime("%Y-%m-%d")
    conn = sqlite3.connect("mikky.db")
    c = conn.cursor()
    c.execute("""
        SELECT id, text, event_time FROM tasks
        WHERE user_id=? AND event_date=?
        ORDER BY event_time
    """, (user_id, today))
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
    c.execute("UPDATE users SET used_messages=? WHERE user_id=?",
              (",".join(map(str, used)), user_id))
    conn.commit()
    conn.close()
    return MESSAGES[idx]

def get_all_active_users():
    """Возвращает всех пользователей с доступом (оплата или триал)"""
    conn = sqlite3.connect("mikky.db")
    c = conn.cursor()
    c.execute("SELECT user_id, first_name, is_paid, trial_start FROM users")
    rows = c.fetchall()
    conn.close()
    result = []
    for user_id, first_name, is_paid_flag, trial_start in rows:
        if is_paid_flag:
            result.append((user_id, first_name))
        elif trial_start:
            start_dt = datetime.fromisoformat(trial_start)
            if start_dt.tzinfo is None:
                start_dt = TIMEZONE.localize(start_dt)
            if (datetime.now(TIMEZONE) - start_dt).days < TRIAL_DAYS:
                result.append((user_id, first_name))
    return result

# ==============================
# ПЛАТЁЖНАЯ КНОПКА (Monobank)
# ==============================
def payment_keyboard(user_id):
    pay_url = "https://send.monobank.ua/jar/5gfL2BGRr3"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить 99 UAH — Monobank", url=pay_url)],
        [InlineKeyboardButton(text="✅ Я оплатил(а)", callback_data=f"check_payment_{user_id}")]
    ])
    return kb

# ==============================
# ХЭНДЛЕРЫ
# ==============================
@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or "друг"

    is_new = get_user(user_id) is None
    create_user(user_id, username, first_name)

    days_left = trial_days_left(user_id)

    await message.answer(
        f"Привет! Я твой новый помощник *Mikky* 🌟\n\n"
        f"Расскажи мне о своих планах!\n\n"
        f"Просто пиши мне:\n"
        f"• 📝 Текстовые заметки\n"
        f"• 📸 Фото\n"
        f"• 🔗 Ссылки\n"
        f"• Дату события, например: _Завтра кофе Лена 15:00_\n\n"
        f"Каждое воскресенье в 17:00 я пришлю план на неделю! 📅",
        parse_mode="Markdown"
    )

    if is_new or days_left > 0:
        await message.answer(
            f"🎁 *7 дней бесплатно!*\n\n"
            f"У тебя есть *{days_left} дн.* бесплатного доступа.\n"
            f"После триала подписка — *99 UAH* 💳",
            parse_mode="Markdown"
        )

@dp.callback_query(F.data.startswith("check_payment_"))
async def check_payment(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[-1])
    await callback.message.answer(
        "⏳ Платёж проверяется...\n\n"
        "После подтверждения я сразу активирую доступ!\n"
        "Если оплатила — напиши /paid"
    )
    await callback.answer()

@dp.message(Command("paid"))
async def manual_paid(message: Message):
    set_paid(message.from_user.id)
    await message.answer("✅ Доступ активирован! Добро пожаловать в Mikky 🎉\n\nТеперь рассказывай о своих планах!")

@dp.message(Command("tasks"))
async def show_tasks(message: Message):
    user_id = message.from_user.id
    if not has_access(user_id):
        days = trial_days_left(user_id)
        if days == 0:
            await message.answer(
                "🔒 Твой бесплатный период закончился!\n\nОформи подписку, чтобы продолжить 👇",
                reply_markup=payment_keyboard(user_id)
            )
        return
    tasks = get_tasks_for_today(user_id)
    if not tasks:
        await message.answer("На сегодня задач нет 🌿")
    else:
        text = "📋 *Твои задачи на сегодня:*\n\n"
        for _, t, time in tasks:
            time_str = f" в {time}" if time else ""
            text += f"• {t}{time_str}\n"
        await message.answer(text, parse_mode="Markdown")

@dp.message(Command("trial"))
async def check_trial(message: Message):
    user_id = message.from_user.id
    user = get_user(user_id)
    if not user:
        await message.answer("Сначала напиши /start")
        return
    if user[3] == 1:
        await message.answer("✅ У тебя активная подписка!")
        return
    days = trial_days_left(user_id)
    if days > 0:
        await message.answer(f"🎁 Осталось *{days} дн.* бесплатного доступа", parse_mode="Markdown")
    else:
        await message.answer(
            "⏰ Бесплатный период закончился!\n\nОформи подписку 👇",
            reply_markup=payment_keyboard(user_id)
        )

@dp.message(F.photo)
async def handle_photo(message: Message):
    user_id = message.from_user.id
    if not has_access(user_id):
        await message.answer("🔒 Бесплатный период закончился!", reply_markup=payment_keyboard(user_id))
        return
    caption = message.caption or "📸 Фото"
    save_task(user_id, caption)
    days = trial_days_left(user_id)
    extra = f"\n_Осталось {days} дн. бесплатного доступа_" if days > 0 and get_user(user_id)[3] == 0 else ""
    await message.answer(f"📸 Сохранила фото в твои планы!{extra}", parse_mode="Markdown")

@dp.message(F.text)
async def handle_text(message: Message):
    user_id = message.from_user.id
    if not has_access(user_id):
        await message.answer(
            "🔒 Твой бесплатный период закончился!\n\nОформи подписку, чтобы продолжить 👇",
            reply_markup=payment_keyboard(user_id)
        )
        return

    text = message.text
    event_date, event_time = parse_datetime(text)
    save_task(user_id, text, event_date, event_time)

    days = trial_days_left(user_id)
    extra = f"\n_Осталось {days} дн. бесплатного доступа_" if days > 0 and get_user(user_id)[3] == 0 else ""

    if event_date:
        await message.answer(
            f"✅ Записала! Напомню {event_date}" + (f" в {event_time}" if event_time else "") + f" 🗓️{extra}",
            parse_mode="Markdown"
        )
    else:
        await message.answer(f"✅ Записала в твои планы!{extra}", parse_mode="Markdown")

# ==============================
# ПАРСИНГ ДАТЫ
# ==============================
def parse_datetime(text):
    import re
    now = datetime.now(TIMEZONE)
    event_date = None
    event_time = None
    text_lower = text.lower()
    if "сегодня" in text_lower:
        event_date = now.strftime("%Y-%m-%d")
    elif "завтра" in text_lower:
        event_date = (now + timedelta(days=1)).strftime("%Y-%m-%d")
    elif "послезавтра" in text_lower:
        event_date = (now + timedelta(days=2)).strftime("%Y-%m-%d")
    time_match = re.search(r'\b(\d{1,2}):(\d{2})\b', text)
    if time_match:
        event_time = time_match.group(0)
    return event_date, event_time

# ==============================
# ПЛАНИРОВЩИК
# ==============================
async def send_weekly_summary():
    users = get_all_active_users()
    for user_id, first_name in users:
        tasks = get_tasks_for_week(user_id)
        msg_of_day = get_unique_message(user_id)
        if not tasks:
            text = (f"📅 *План на следующую неделю*\n\n"
                    f"Пока задач нет — расскажи мне о планах!\n\n"
                    f"_{msg_of_day}_")
        else:
            text = f"📅 *План на следующую неделю, {first_name}!*\n\n"
            for task_text, date, time in tasks:
                time_str = f" в {time}" if time else ""
                text += f"• {date}{time_str} — {task_text}\n"
            text += f"\n_{msg_of_day}_"
        try:
            await bot.send_message(user_id, text, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Ошибка отправки {user_id}: {e}")

async def send_morning_reminders():
    users = get_all_active_users()
    for user_id, first_name in users:
        tasks = get_tasks_for_today(user_id)
        if not tasks:
            continue
        msg_of_day = get_unique_message(user_id)
        text = f"🌅 Привет, *{first_name}*!\n\n*Твои задачи на сегодня:*\n\n"
        for _, task_text, time in tasks:
            time_str = f" в {time}" if time else ""
            text += f"• {task_text}{time_str}\n"
        text += f"\n_{msg_of_day}_"
        try:
            await bot.send_message(user_id, text, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Ошибка: {e}")

async def send_30min_reminders():
    now = datetime.now(TIMEZONE)
    target_time = (now + timedelta(minutes=30)).strftime("%H:%M")
    today = now.strftime("%Y-%m-%d")
    conn = sqlite3.connect("mikky.db")
    c = conn.cursor()
    c.execute("""
        SELECT tasks.id, tasks.user_id, tasks.text, users.first_name
        FROM tasks JOIN users ON tasks.user_id = users.user_id
        WHERE tasks.event_date=? AND tasks.event_time=? AND tasks.notified_30min=0
    """, (today, target_time))
    rows = c.fetchall()
    for task_id, user_id, task_text, first_name in rows:
        if not has_access(user_id):
            continue
        try:
            await bot.send_message(
                user_id,
                f"⏰ *{first_name}*, через 30 минут:\n\n_{task_text}_",
                parse_mode="Markdown"
            )
            c.execute("UPDATE tasks SET notified_30min=1 WHERE id=?", (task_id,))
        except Exception as e:
            logging.error(f"Ошибка: {e}")
    conn.commit()
    conn.close()

async def notify_trial_ending():
    """За 1 день до конца триала — напомнить об оплате"""
    conn = sqlite3.connect("mikky.db")
    c = conn.cursor()
    c.execute("SELECT user_id, first_name, trial_start FROM users WHERE is_paid=0")
    rows = c.fetchall()
    conn.close()
    for user_id, first_name, trial_start in rows:
        if not trial_start:
            continue
        start_dt = datetime.fromisoformat(trial_start)
        if start_dt.tzinfo is None:
            start_dt = TIMEZONE.localize(start_dt)
        days_elapsed = (datetime.now(TIMEZONE) - start_dt).days
        if days_elapsed == TRIAL_DAYS - 1:
            try:
                await bot.send_message(
                    user_id,
                    f"⏰ *{first_name}*, завтра заканчивается бесплатный период!\n\n"
                    f"Оформи подписку, чтобы продолжить пользоваться Mikky 💛",
                    parse_mode="Markdown",
                    reply_markup=payment_keyboard(user_id)
                )
            except Exception as e:
                logging.error(f"Ошибка: {e}")

# ==============================
# ЗАПУСК
# ==============================
async def main():
    init_db()
    scheduler.add_job(send_weekly_summary, "cron", day_of_week="sun", hour=17, minute=0)
    scheduler.add_job(send_morning_reminders, "cron", hour=8, minute=0)
    scheduler.add_job(send_30min_reminders, "interval", minutes=5)
    scheduler.add_job(notify_trial_ending, "cron", hour=10, minute=0)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
