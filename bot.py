import asyncio  
import logging  
import random  
from datetime import datetime, timedelta  
import pytz  
import re  
  
import aiosqlite  
from aiogram import Bot, Dispatcher, types, F  
from aiogram.filters import Command  
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton  
from aiogram.fsm.storage.memory import MemoryStorage  
from apscheduler.schedulers.asyncio import AsyncIOScheduler  
  
# ============================================================  
# НАСТРОЙКИ  
# ============================================================  
BOT_TOKEN = "8988206711:AAGmjkJ0t-hz0iU1cDmIgsXK9sXvxk6xJzg"  
  
ADMIN_ID = 7756969434  
MONOBANK_LINK = "https://send.monobank.ua/jar/5gfL2BGRr3"  
  
TIMEZONE = "Europe/Kiev"  
DB_NAME = "miky.db"  
FREE_DAYS = 7  
# ============================================================  
  
logging.basicConfig(level=logging.INFO)  
  
bot = Bot(token=BOT_TOKEN)  
dp = Dispatcher(storage=MemoryStorage())  
scheduler = AsyncIOScheduler(timezone=TIMEZONE)  
tz = pytz.timezone(TIMEZONE)  
  
# ============================================================  
# МОТИВАЦИОННЫЕ СООБЩЕНИЯ  
# ============================================================  
MESSAGES_LIST = [  
    "Лучшее время начать — сейчас, а не завтра.", "Маленькие шаги каждый день приводят к большим результатам.",  
    "Не жди идеального момента — действуй, имея то, что есть.", "Страх — это лишь сигнал, что ты на пороге чего-то важного.",  
    "Одна попытка стоит больше, чем сто сожалений.", "Дорогу осилит идущий, даже если он идет медленно.",  
    "Твои действия громче твоих слов.", "Сделай первый шаг, и путь появится сам.",  
    "Не бойся ошибаться — бойся стоять на месте.", "Каждый новый день — это чистый лист. Напиши свою историю.",  
    "Двигайся, даже если кажется, что нет сил.", "Начни с того, что есть, сделай то, что можешь.",  
    "Лучше сделать и пожалеть, чем не сделать и жалеть всю жизнь.", "Возьми ответственность за свою жизнь в свои руки.",  
    "Мысль без действия — всего лишь мечта.", "Ты способен на гораздо большее, чем думаешь.",  
    "Никто не может заставить тебя чувствовать себя неполноценным без твоего согласия.",  
    "Сравнивай себя только с собой вчерашним.", "Твоя ценность не зависит от мнения других людей.",  
    "Ты — автор своей жизни, не будь просто читателем.", "Доверяй своему внутреннему голосу.",  
    "У тебя есть всё необходимое, чтобы добиться успеха.", "Ты уникален, и в этом твоя сила.",  
    "Перестань искать одобрения — найди себя.", "Верь в свою идею, даже если никто не верит.",  
    "Твоё прошлое — не приговор. Это опыт.", "Ты уже пережил 100% своих плохих дней.",  
    "Не уменьшай свою ценность, чтобы угодить другим.", "Прими свои недостатки — они делают тебя настоящим.",  
    "Ты достоин счастья, успеха и любви.", "После дождя всегда приходит радуга.",  
    "Падать не страшно — страшно не подниматься.", "Любая неудача — это урок, а не финал.",  
    "Трудности делают тебя сильнее.", "Стена стоит только на пути тех, кто не хочет её обойти.",  
    "Самые сильные люди рождаются из самых сложных ситуаций.", "Сдаться — это единственный способ проиграть.",  
    "В конце каждой туннеля есть свет, просто нужно продолжать идти.", "Не проблема важна, а твоя реакция на неё.",  
    "Разреши себе быть несовершенным, но настойчивым.", "Всё, что тебя не убивает, делает тебя мудрее.",  
    "Твой предел — это только то, что ты сам себе установил.", "Вместо «Почему это случилось со мной?» спроси «Чему это меня учит?».",  
    "Самая большая слава — не в том, чтобы никогда не падать, а в том, чтобы вставать каждый раз.",  
    "Шторм заканчивается, и море снова становится спокойным.", "Капля камень точит не силой, а частотой падения.",  
    "Дисциплина — это мост между целями и их достижением.", "Система важнее, чем мотивация.",  
    "Делай сегодня то, что другие не хотят, чтобы завтра жить так, как другие не могут.",  
    "Поставь цель и не отвлекайся на шум.", "1% улучшения каждый день = 3700% в год.",  
    "Упорство побеждает талант, если талант не упорен.", "Сфокусируйся на процессе, результат придет сам.",  
    "Легких путей к великим целям не бывает.", "Твоя зона комфорта — враг твоего роста.",  
    "Иди к цели с упорством голодного волка.", "Каждый пропущенный день — это шаг назад.",  
    "Сначала ты работаешь на свою репутацию, потом репутация работает на тебя.",  
    "Не откладывай жизнь на потом — живи сейчас, достигай сейчас.", "Терпение — это не пассивность, это сила выдержки.",  
    "Мир полон возможностей, нужно только открыть глаза.", "Твои мысли формируют твою реальность.",  
    "Окружай себя теми, кто поднимает тебя вверх.", "Читай. Учись. Расти. Повторяй.",  
    "Позитивное мышление притягивает позитивные события.", "Вдохновение — это гость, который не любит посещать ленивых.",  
    "Знание — это сила, а применение знания — суперсила.", "Будь благодарен за то, что имеешь, пока стремишься к большему.",  
    "Ты — это среднее из пяти людей, с которыми проводишь больше всего времени.",  
    "Инвестируй в себя — это единственное вложение, которое всегда окупается.",  
    "Креативность — это просто соединение вещей.", "Любопытство — двигатель прогресса.",  
    "Будь тем изменением, которое хочешь видеть в мире.", "Учись видеть хорошее в каждом дне.",  
    "Мечты сбываются, когда ты перестаешь просто мечтать и начинаешь делать.",  
    "Отдавай миру больше, чем берёшь.", "Искренность — самая сильная валюта.",  
    "Умение слушать — редкий дар. Используй его.", "Помощь другим — лучший способ помочь себе.",  
    "Создавай связи, а не контакты.", "Делай добро, и оно к тебе вернётся.",  
    "Цени людей, которые верят в тебя, когда ты сам в себя не веришь.",  
    "Твой успех — это успех твоей команды.", "Прощение — это не слабость, это освобождение.",  
    "Будь лидером, а не начальником.", "Слово может ранить, но может и вдохновить. Выбирай мудро.",  
    "Вдохновляй своим примером.", "Поддерживай других на их пути, и твой путь станет легче.",  
    "Не суди людей, пока не прошел милю в их ботинках.", "Каждый человек несёт свою историю — будь добр.",  
    "Улыбка — это самый короткий путь между двумя людьми.", "Настоящая дружба проверяется в трудные времена.",  
    "Люби себя достаточно, чтобы требовать уважения.", "Твоё время — самый ценный ресурс. Трать его мудро.",  
    "Сегодняшний день больше не повторится. Сделай его значимым.", "Маленькие победы складываются в большой успех.",  
    "Живи так, чтобы вспоминать с улыбкой.", "Ты сильнее, чем кажешься, и умнее, чем думаешь.",  
    "Каждый шаг вперёд — это победа над вчерашним собой."  
]  
  
# ============================================================  
# БАЗА ДАННЫХ  
# ============================================================  
async def init_db():  
    async with aiosqlite.connect(DB_NAME) as db:  
        await db.execute("""CREATE TABLE IF NOT EXISTS users (  
            user_id INTEGER PRIMARY KEY,  
            username TEXT,  
            first_name TEXT,  
            is_paid INTEGER DEFAULT 0,  
            paid_until TEXT,  
            joined_at TEXT  
        )""")  
        await db.execute("""CREATE TABLE IF NOT EXISTS events (  
            id INTEGER PRIMARY KEY AUTOINCREMENT,  
            user_id INTEGER,  
            text TEXT,  
            event_date TEXT,  
            event_time TEXT,  
            reminded_morning INTEGER DEFAULT 0,  
            reminded_30min INTEGER DEFAULT 0,  
            created_at TEXT  
        )""")  
        await db.execute("""CREATE TABLE IF NOT EXISTS sent_quotes (  
            user_id INTEGER,  
            quote_index INTEGER,  
            UNIQUE(user_id, quote_index)  
        )""")  
        await db.commit()  
  
async def get_user(user_id: int):  
    async with aiosqlite.connect(DB_NAME) as db:  
        async with db.execute("SELECT * FROM users WHERE user_id=?", (user_id,)) as cursor:  
            return await cursor.fetchone()  
  
async def is_paid(user_id: int) -> bool:  
    if user_id == ADMIN_ID:  
        return True  
    user = await get_user(user_id)  
    if not user or user[3] != 1 or not user[4]:  
        return False  
    now = datetime.now(tz).strftime("%Y-%m-%d")  
    return user[4] >= now  
  
async def register_user(user_id: int, username: str = None, first_name: str = None):  
    async with aiosqlite.connect(DB_NAME) as db:  
        paid_until = (datetime.now(tz) + timedelta(days=FREE_DAYS)).strftime("%Y-%m-%d")  
        await db.execute(  
            """INSERT OR IGNORE INTO users   
               (user_id, username, first_name, is_paid, paid_until, joined_at)   
               VALUES (?,?,?,?,?,?)""",  
            (user_id, username, first_name, 1, paid_until, datetime.now(tz).isoformat())  
        )  
        await db.commit()  
    return paid_until  
  
async def activate_user(user_id: int):  
    paid_until = (datetime.now(tz) + timedelta(days=30)).strftime("%Y-%m-%d")  
    async with aiosqlite.connect(DB_NAME) as db:  
        await db.execute("UPDATE users SET is_paid=1, paid_until=? WHERE user_id=?", (paid_until, user_id))  
        await db.commit()  
    return paid_until  
  
async def get_random_quote(user_id: int):  
    async with aiosqlite.connect(DB_NAME) as db:  
        async with db.execute("SELECT quote_index FROM sent_quotes WHERE user_id=?", (user_id,)) as cursor:  
            used = [row[0] for row in await cursor.fetchall()]  
        available = [i for i in range(len(MESSAGES_LIST)) if i not in used]  
        if not available:  
            await db.execute("DELETE FROM sent_quotes WHERE user_id=?", (user_id,))  
            await db.commit()  
            available = list(range(len(MESSAGES_LIST)))  
        idx = random.choice(available)  
        await db.execute("INSERT OR IGNORE INTO sent_quotes VALUES (?,?)", (user_id, idx))  
        await db.commit()  
        return MESSAGES_LIST[idx]  
  
async def save_event(user_id: int, text: str, event_date=None, event_time=None):  
    async with aiosqlite.connect(DB_NAME) as db:  
        await db.execute(  
            "INSERT INTO events (user_id, text, event_date, event_time, created_at) VALUES (?,?,?,?,?)",  
            (user_id, text, event_date, event_time, datetime.now(tz).isoformat())  
        )  
        await db.commit()  
  
async def get_week_events(user_id: int):  
    async with aiosqlite.connect(DB_NAME) as db:  
        today = datetime.now(tz).date()  
        week_end = today + timedelta(days=7)  
        async with db.execute(  
            "SELECT text, event_date, event_time FROM events WHERE user_id=? AND event_date BETWEEN ? AND ? ORDER BY event_date, event_time",  
            (user_id, today.strftime("%Y-%m-%d"), week_end.strftime("%Y-%m-%d"))  
        ) as cursor:  
            return await cursor.fetchall()  
  
async def get_today_events(user_id: int):  
    async with aiosqlite.connect(DB_NAME) as db:  
        today = datetime.now(tz).strftime("%Y-%m-%d")  
        async with db.execute(  
            "SELECT id, text, event_time FROM events WHERE user_id=? AND event_date=? ORDER BY event_time",  
            (user_id, today)  
        ) as cursor:  
            return await cursor.fetchall()  
  
async def get_all_paid_users():  
    async with aiosqlite.connect(DB_NAME) as db:  
        today = datetime.now(tz).strftime("%Y-%m-%d")  
        async with db.execute(  
            "SELECT user_id, username, first_name FROM users WHERE is_paid=1 AND paid_until>=?", (today,)  
        ) as cursor:  
            return await cursor.fetchall()  
  
# ============================================================  
# ПАРСИНГ ДАТЫ  
# ============================================================  
def parse_datetime(text):  
    text_lower = text.lower()  
    today = datetime.now(tz).date()  
    event_date = None  
    event_time = None  
  
    time_match = re.search(r'\b(\d{1,2})[:\.](\d{2})\b', text)  
    if time_match:  
        h, m = int(time_match.group(1)), int(time_match.group(2))  
        if 0 <= h <= 23 and 0 <= m <= 59:  
            event_time = f"{h:02d}:{m:02d}"  
  
    if "сегодня" in text_lower:  
        event_date = today.strftime("%Y-%m-%d")  
    elif "завтра" in text_lower:  
        event_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")  
    elif "послезавтра" in text_lower:  
        event_date = (today + timedelta(days=2)).strftime("%Y-%m-%d")  
  
    days_map = {"понедельник":0, "вторник":1, "среда":2, "среду":2, "четверг":3, "пятница":4, "пятницу":4,  
                "суббота":5, "субботу":5, "воскресенье":6}  
    if not event_date:  
        for day_name, day_num in days_map.items():  
            if day_name in text_lower:  
                diff = (day_num - today.weekday()) % 7  
                if diff == 0: diff = 7  
                event_date = (today + timedelta(days=diff)).strftime("%Y-%m-%d")  
                break  
    return event_date, event_time  
  
# ============================================================  
# ХЕНДЛЕРЫ  
# ============================================================  
@dp.message(Command("start"))  
async def cmd_start(msg: Message):  
    paid_until = await register_user(msg.from_user.id, msg.from_user.username, msg.from_user.first_name)  
    name = msg.from_user.first_name or msg.from_user.username or "друг"  
    await msg.answer(  
        f"👋 Привет, {name}!\n\n"  
        f"🎉 Тебе активировано **{FREE_DAYS} дней бесплатно** до {paid_until}!\n\n"  
        f"Просто пиши мне о планах — я запомню и напомню 🐕",  
        parse_mode="Markdown"  
    )  
  
@dp.message(Command("pay"))  
async def cmd_pay(msg: Message):  
    kb = InlineKeyboardMarkup(inline_keyboard=[  
        [InlineKeyboardButton(text="💳 Оплатить 50 грн", url=MONOBANK_LINK)],  
        [InlineKeyboardButton(text="✅ Я оплатил(а)", callback_data=f"paid_{msg.from_user.id}")]  
    ])  
    await msg.answer("💰 *Продление подписки*\n\nЦена: 50 грн / месяц", parse_mode="Markdown", reply_markup=kb)  
  
@dp.callback_query(F.data.startswith("paid_"))  
async def cb_paid(callback: types.CallbackQuery):  
    user_id = int(callback.data.split("_")[1])  
    kb = InlineKeyboardMarkup(inline_keyboard=[  
        [InlineKeyboardButton(text="✅ Активировать", callback_data=f"activate_{user_id}")],  
        [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{user_id}")]  
    ])  
    await bot.send_message(ADMIN_ID, f"💰 Запрос на оплату!\nID: `{user_id}`", parse_mode="Markdown", reply_markup=kb)  
    await callback.answer("Отправлено")  
  
@dp.callback_query(F.data.startswith("activate_"))  
async def cb_activate(callback: types.CallbackQuery):  
    if callback.from_user.id != ADMIN_ID: return  
    user_id = int(callback.data.split("_")[1])  
    paid_until = await activate_user(user_id)  
    await bot.send_message(user_id, f"🎉 Подписка продлена до {paid_until}!", parse_mode="Markdown")  
    await callback.message.edit_text(f"✅ Продлено до {paid_until}")  
  
@dp.callback_query(F.data.startswith("reject_"))  
async def cb_reject(callback: types.CallbackQuery):  
    if callback.from_user.id != ADMIN_ID: return  
    user_id = int(callback.data.split("_")[1])  
    await bot.send_message(user_id, "❌ Оплата не подтверждена.")  
    await callback.message.edit_text("❌ Отклонено")  
  
@dp.message(Command("plans"))  
async def cmd_plans(msg: Message):  
    if not await is_paid(msg.from_user.id):  
        await msg.answer("🔒 Доступно только после оплаты. Напиши /pay")  
        return  
    events = await get_week_events(msg.from_user.id)  
    if not events:  
        await msg.answer("📭 Планов на неделю нет.")  
        return  
    text = "📅 *Планы на неделю:*\n\n" + "\n".join([f"• {ev[0]} — {ev[1]}" + (f" в {ev[2]}" if ev[2] else "") for ev in events])  
    await msg.answer(text, parse_mode="Markdown")  
  
@dp.message(Command("today"))  
async def cmd_today(msg: Message):  
    if not await is_paid(msg.from_user.id):  
        await msg.answer("🔒 Доступно только после оплаты. Напиши /pay")  
        return  
    events = await get_today_events(msg.from_user.id)  
    if not events:  
        await msg.answer("📭 На сегодня планов нет.")  
        return  
    text = "📋 *Задачи на сегодня:*\n\n" + "\n".join([f"• {ev[1]}" + (f" в {ev[2]}" if ev[2] else "") for ev in events])  
    await msg.answer(text, parse_mode="Markdown")  
  
@dp.message()  
async def handle_any(msg: Message):  
    if not await is_paid(msg.from_user.id):  
        await msg.answer("🔒 Для сохранения планов нужна подписка — /pay")  
        return  
    text = msg.text or msg.caption or "[медиа]"  
    event_date, event_time = parse_datetime(text)  
    await save_event(msg.from_user.id, text, event_date, event_time)  
    reply = "✅ Записала!"  
    if event_date:  
        reply += f" {event_date}"  
        if event_time: reply += f" в {event_time}"  
    await msg.answer(reply)  
  
# ============================================================  
# ПЛАНИРОВЩИК  
# ============================================================  
async def send_morning_summary(user_id: int):  
    events = await get_today_events(user_id)  
    user = await get_user(user_id)  
    name = user[2] if user else "друг"  
    quote = await get_random_quote(user_id)  
    if not events:  
        text = f"🌅 Доброе утро, *{name}*!\n\n📭 Планов нет\n\n💫 *Послание дня:*\n_{quote}_"  
    else:  
        task_list = "\n".join([f"• {ev[1]}" + (f" в {ev[2]}" if ev[2] else "") for ev in events])  
        text = f"🌅 Доброе утро, *{name}*!\n\n📋 Задачи:\n{task_list}\n\n💫 *Послание дня:*\n_{quote}_"  
    await bot.send_message(user_id, text, parse_mode="Markdown")  
  
async def morning_job():  
    users = await get_all_paid_users()  
    for user in users:  
        try:  
            await send_morning_summary(user[0])  
        except Exception as e:  
            logging.error(f"Morning error {user[0]}: {e}")  
  
async def reminder_30min_job():  
    async with aiosqlite.connect(DB_NAME) as db:  
        now = datetime.now(tz)  
        target = (now + timedelta(minutes=30)).strftime("%H:%M")  
        today = now.strftime("%Y-%m-%d")  
        async with db.execute(  
            "SELECT id, user_id, text FROM events WHERE event_date=? AND event_time=? AND reminded_30min=0",  
            (today, target)  
        ) as cursor:  
            rows = await cursor.fetchall()  
        for row in rows:  
            event_id, user_id, text = row  
            if await is_paid(user_id):  
                await bot.send_message(user_id, f"⏰ Через 30 минут:\n{text}", parse_mode="Markdown")  
                await db.execute("UPDATE events SET reminded_30min=1 WHERE id=?", (event_id,))  
        await db.commit()  
  
async def weekly_plan_job():  
    users = await get_all_paid_users()  
    for user in users:  
        try:  
            events = await get_week_events(user[0])  
            name = user[2] or "друг"  
            if not events:  
                text = f"📅 {name}, планов на неделю пока нет."  
            else:  
                task_list = "\n".join([f"• {ev[0]} — {ev[1]}" + (f" в {ev[2]}" if ev[2] else "") for ev in events])  
                text = f"📅 План на неделю для {name}:\n\n{task_list}"  
            await bot.send_message(user[0], text, parse_mode="Markdown")  
        except Exception as e:  
            logging.error(f"Weekly error: {e}")  
  
# ============================================================  
# ЗАПУСК  
# ============================================================  
async def main():  
    await init_db()  
    scheduler.add_job(morning_job, "cron", hour=8, minute=0)  
    scheduler.add_job(reminder_30min_job, "interval", minutes=1)  
    scheduler.add_job(weekly_plan_job, "cron", day_of_week="sun", hour=17, minute=0)  
    scheduler.start()  
    await dp.start_polling(bot)  
  
if __name__ == "__main__":  
    asyncio.run(main())  
