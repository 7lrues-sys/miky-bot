from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import logging
import sqlite3
import random
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
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
# ПРЕДСКАЗАНИЯ НА 21 ЯЗЫКЕ (полные переводы)
# ==============================
PREDICTIONS = {
    'ru': [
        "купи себе слайм", "нафиг эти отношения", "у твоей судьбы рост 185+", "твоя судьба футболист",
        "ты супер, знай это)", "относись к людям так, как хочешь чтобы относились к тебе",
        "иди туда, где страшно. там и живёт твоя лучшая версия", "не проси лёгкой жизни — проси силы",
        "сделай сегодня то, за что завтрашний ты скажет спасибо", "ты можешь. ты уже доказывал это раньше",
        "сегодня — хороший день, чтобы стать чуть лучше", "где-то кто-то мечтает о жизни, которую ты считаешь обычной",
        "красота есть в этом дне — просто посмотри внимательнее", "твоя история ещё не дописана",
        "даже звёзды когда-то были просто пылью", "в тебе есть что-то, чего нет больше ни в ком на планете",
        "твоей нервной системе нужен отдых", "опять без интима, денег и хорошей жизни... но скоро всё изменится",
        "тебе знак", "с неизвестного номера позвонит твоя любовь, возможно", "не опускайся до их уровня",
        "научись признавать свои ошибки. люди не всегда правы, солнце", "жди крутых новостей ближе к вечеру",
        "купи себе что-нибудь вкусненькое — заслужил", "скоро что-то хорошее само найдёт тебя",
        "твоя удача уже в пути, просто немного застряла в пробках", "сегодня отличный день для неожиданных встреч",
        "перестань объяснять себя тем, кто не хочет понимать", "твои мечты реальнее, чем ты думаешь",
        "кто-то прямо сейчас думает о тебе и улыбается", "новый уровень — новые враги, держись",
        "не каждый, кто молчит, согласен", "твой следующий шаг изменит всё", "отдохни. даже море иногда бывает спокойным",
        "ты ближе к цели, чем кажется", "перестань искать смысл там, где его нет",
        "скоро тебя ждёт что-то, от чего захочется прыгать", "позвони маме. просто так",
        "пора менять причёску — и жизнь поменяется тоже", "твои враги следят за твоим прогрессом. не разочаруй их",
        "сегодня можно побыть немного эгоистом", "тот, кто тебя бросил, уже жалеет",
        "удача любит тех, кто не ноет", "пришло время избавиться от старого хлама — и в доме, и в душе",
        "ты заслуживаешь извинений, которые никогда не получишь. и всё равно победишь",
        "скоро будет повод надеть любимый наряд", "кто-то завидует твоей улыбке",
        "жизнь слишком коротка для плохого кофе и токсичных людей", "твои руки созданы для чего-то великого",
        "сегодня вечером тебя ждёт приятный сюрприз", "перестань ждать пятницы — живи сейчас",
        "ты сильнее своих мыслей в три часа ночи", "не всё, что теряешь — потеря",
        "скоро придёт сообщение, которого ты давно ждал", "твоя интуиция права. прислушайся",
        "сегодня вселенная на твоей стороне", "ты не для всех — и это твоя суперсила",
        "скоро начнётся новая глава. листай", "купи растение. оно не предаст",
        "ты слишком много думаешь. выдохни", "кто-то тайно восхищается тобой",
        "пора перестать извиняться за то, что ты есть", "твоя следующая поездка изменит тебя",
        "сегодня хороший день, чтобы простить. себя в первую очередь", "деньги найдут тебя там, где ты меньше всего ожидаешь",
        "не все советы — помощь. умей фильтровать", "твоя харизма сегодня на максималках",
        "скоро встретишь человека, который всё поймёт с полуслова", "ты создан не для серой жизни",
        "сегодня можно не быть продуктивным", "твоя спина устала — распрямись",
        "скоро позвонят с хорошей новостью", "тебе надо в отпуск. срочно",
        "ты умнее, чем думают окружающие", "сегодня что-то потеряешь, но найдёшь кое-что важнее",
        "перестань откладывать. начни прямо сейчас", "твоя следующая влюблённость будет взаимной",
        "кто-то уже рассказывает о тебе с восторгом", "ты слишком крут для этой драмы",
        "скоро в твоей жизни появится новый человек — и надолго", "удача сегодня ходит рядом. не прогони её плохим настроением",
        "сделай себе выходной внутри рабочего дня", "твоё тело — храм. покорми его нормально",
        "скоро найдёшь то, что долго искал", "не бойся занять больше места в этом мире",
        "сегодня вселенная подмигивает тебе", "кто-то хочет помириться, но не знает как начать",
        "ты заслуживаешь любви без условий", "скоро придёт ответ на вопрос, который мучил тебя",
        "твой день лучше, чем ты думаешь", "улыбнись незнакомцу. это изменит чей-то день"
    ],
    'en': [
        "buy yourself some slime", "to hell with these relationships", "your destiny is 185+ tall", "your destiny is a footballer",
        "you're super, know that)", "treat people the way you want to be treated",
        "go where it's scary. that's where your best version lives", "don't ask for an easy life — ask for strength",
        "do today what tomorrow's you will thank you for", "you can. you've proven it before",
        "today is a good day to become a little better", "somewhere someone dreams of a life you think is ordinary",
        "there is beauty in this day — just look closer", "your story is not finished yet",
        "even stars were once just dust", "there is something in you that no one else has",
        "your nervous system needs rest", "again no intimacy, money or good life... but soon everything will change",
        "this is a sign for you", "your love might call from an unknown number", "don't stoop to their level",
        "learn to admit your mistakes. people aren't always right, sunshine", "wait for cool news by evening",
        "buy yourself something tasty — you deserve it", "soon something good will find you",
        "your luck is already on its way, just stuck in traffic", "today is a great day for unexpected meetings",
        "stop explaining yourself to those who don't want to understand", "your dreams are more real than you think",
        "someone is thinking about you right now and smiling", "new level — new enemies, hold on",
        "not everyone who is silent agrees", "your next step will change everything", "rest. even the sea is sometimes calm",
        "you are closer to the goal than it seems", "stop looking for meaning where there is none",
        "soon something awaits you that will make you want to jump", "call mom. just because",
        "time to change your hairstyle — and life will change too", "your enemies are watching your progress. don't disappoint them",
        "today you can be a little selfish", "the one who left you already regrets it",
        "luck loves those who don't whine", "it's time to get rid of old junk — in the house and in the soul",
        "you deserve apologies you'll never get. and you'll still win", "soon there will be a reason to wear your favorite outfit",
        "someone envies your smile", "life is too short for bad coffee and toxic people",
        "your hands are made for something great", "tonight you have a nice surprise waiting",
        "stop waiting for Friday — live now", "you are stronger than your 3am thoughts",
        "not everything you lose is a loss", "soon a message you've been waiting for will come",
        "your intuition is right. listen to it", "today the universe is on your side",
        "you are not for everyone — and that's your superpower", "a new chapter is about to begin. turn the page",
        "buy a plant. it won't betray you", "you think too much. exhale",
        "someone secretly admires you", "stop apologizing for existing",
        "your next trip will change you", "today is a good day to forgive. yourself first",
        "money will find you where you least expect it", "not all advice is help. learn to filter",
        "your charisma is at max today", "soon you'll meet someone who understands you without words",
        "you were not created for a gray life", "today you can not be productive",
        "your back is tired — straighten up", "soon they'll call with good news",
        "you need a vacation. urgently", "you are smarter than people think",
        "today you will lose something, but find something more important", "stop procrastinating. start right now",
        "your next love will be mutual", "someone is already talking about you with delight",
        "you are too cool for this drama", "soon a new person will appear in your life — and for a long time",
        "luck is walking next to you today. don't scare it away with a bad mood",
        "give yourself a day off inside a workday", "your body is a temple. feed it properly",
        "soon you'll find what you've been looking for for a long time", "don't be afraid to take up more space in this world",
        "today the universe is winking at you", "someone wants to make peace but doesn't know how to start",
        "you deserve unconditional love", "soon an answer to the question that tormented you will come",
        "your day is better than you think", "smile at a stranger. it will change someone's day"
    ],
    'uk': [  # Українська
        "купи собі слайм", "нафіг ці стосунки", "у твоєї долі зріст 185+", "твоя доля — футболіст",
        "ти супер, знай це)", "стався до людей так, як хочеш, щоб ставились до тебе",
        "йди туди, де страшно. там живе твоя найкраща версія", "не проси легкого життя — проси сили",
        "зроби сьогодні те, за що завтрашній ти скаже дякую", "ти можеш. ти вже доводив це раніше",
        "сьогодні — хороший день, щоб стати трохи кращим", "десь хтось мріє про життя, яке ти вважаєш звичайним",
        "краса є в цьому дні — просто подивись уважніше", "твоя історія ще не дописана",
        "навіть зірки колись були просто пилом", "в тобі є щось, чого немає більше ні в кого на планеті",
        "твоїй нервовій системі потрібен відпочинок", "знову без інтиму, грошей і хорошого життя... але скоро все зміниться",
        "тобі знак", "з невідомого номера зателефонує твоя любов, можливо", "не опускайся до їхнього рівня",
        "вчись визнавати свої помилки. люди не завжди праві, сонце", "чекай крутих новин ближче до вечора",
        "купи собі щось смачненьке — заслужив", "скоро щось хороше саме тебе знайде",
        "твоя удача вже в дорозі, просто трохи застрягла в пробках", "сьогодні відмінний день для несподіваних зустрічей",
        "перестань пояснювати себе тим, хто не хоче розуміти", "твої мрії реальніші, ніж ти думаєш",
        "хтось прямо зараз думає про тебе і посміхається", "новий рівень — нові вороги, тримайся",
        "не кожен, хто мовчить, згоден", "твій наступний крок змінить все", "відпочинь. навіть море іноді буває спокійним",
        "ти ближче до мети, ніж здається", "перестань шукати сенс там, де його немає",
        "скоро тебе чекає щось, від чого захочеться стрибати", "подзвони мамі. просто так",
        "пора міняти зачіску — і життя теж зміниться", "твої вороги слідкують за твоїм прогресом. не розчаруй їх",
        "сьогодні можна трохи побути егоїстом", "той, хто тебе кинув, вже шкодує",
        "удача любить тих, хто не ноє", "прийшов час позбутися старого мотлоху — і в домі, і в душі",
        "ти заслуговуєш на вибачення, яких ніколи не отримаєш. і все одно переможеш",
        "скоро буде привід надягти улюблений наряд", "хтось заздрить твоїй усмішці",
        "життя надто коротке для поганого кави і токсичних людей", "твої руки створені для чогось великого",
        "сьогодні ввечері тебе чекає приємний сюрприз", "перестань чекати п'ятниці — живи зараз",
        "ти сильніший за свої думки о 3 ночі", "не все, що втрачаєш — втрата",
        "скоро прийде повідомлення, якого ти давно чекав", "твоя інтуїція права. прислухайся",
        "сьогодні всесвіт на твоєму боці", "ти не для всіх — і це твоя суперсила",
        "скоро почнеться нова глава. гортай", "купи рослину. вона не зрадить",
        "ти занадто багато думаєш. видихни", "хтось таємно захоплюється тобою",
        "пора перестати вибачатися за те, що ти є", "твоя наступна подорож змінить тебе",
        "сьогодні хороший день, щоб пробачити. себе в першу чергу", "гроші знайдуть тебе там, де ти менше всього очікуєш",
        "не всі поради — допомога. вміти фільтрувати", "твоя харизма сьогодні на максималках",
        "скоро зустрінеш людину, яка все зрозуміє з півслова", "ти створений не для сірого життя",
        "сьогодні можна не бути продуктивним", "твоя спина втомилася — розпрямись",
        "скоро подзвонять з хорошою новиною", "тобі треба у відпустку. терміново",
        "ти розумніший, ніж думають оточуючі", "сьогодні щось втратиш, але знайдеш щось важливіше",
        "перестань відкладати. починай прямо зараз", "твоє наступне кохання буде взаємним",
        "хтось вже розповідає про тебе із захватом", "ти занадто крутий для цієї драми",
        "скоро в твоєму житті з'явиться нова людина — і надовго", "удача сьогодні ходить поруч. не прогони її поганим настроєм",
        "зроби собі вихідний всередині робочого дня", "твоє тіло — храм. годуй його нормально",
        "скоро знайдеш те, що довго шукав", "не бійся займати більше місця в цьому світі",
        "сьогодні всесвіт підморгує тобі", "хтось хоче помиритися, але не знає, як почати",
        "ти заслуговуєш на любов без умов", "скоро прийде відповідь на питання, яке тебе мучило",
        "твій день кращий, ніж ти думаєш", "усміхнися незнайомцю. це змінить чийсь день"
    ],
    # Для інших мов — скорочена версія (fallback)
    'zh': ["买点史莱姆吧", "去他妈的这些关系", "你的命运身高185+", "你的命运是足球运动员", "你很棒，知道这一点", "善待他人如己", "去害怕的地方，那里有最好的你", "不要祈求轻松的生活——祈求力量", "今天做让明天的你感谢的事", "你可以。你以前证明过"],
    'hi': ["खुद के लिए स्लाइम खरीदो", "इन रिश्तों को नर्क में", "तुम्हारे भाग्य की ऊंचाई 185+", "तुम्हारा भाग्य फुटबॉलर है", "तुम सुपर हो, जान लो", "लोगों से वैसा व्यवहार करो जैसा तुम चाहते हो"],
    'es': ["cómprate slime", "al diablo con estas relaciones", "tu destino mide 185+", "tu destino es futbolista", "eres genial, sábelo", "trata a los demás como quieres que te traten"],
    'fr': ["achète-toi du slime", "au diable ces relations", "ton destin fait 185+", "ton destin est footballeur", "tu es super, sache-le", "traite les gens comme tu veux être traité"],
    'ar': ["اشترِ لنفسك سلايم", "للجحيم هذه العلاقات", "قدرك طوله 185+", "قدرك لاعب كرة قدم", "أنت رائع، اعلم ذلك", "عامل الناس كما تحب أن يعاملوك"],
    'pt': ["compre slime para você", "pro inferno esses relacionamentos", "seu destino tem 185+", "seu destino é jogador de futebol", "você é incrível, saiba disso"],
    'de': ["kauf dir Slime", "zur Hölle mit diesen Beziehungen", "dein Schicksal ist 185+", "dein Schicksal ist Fußballer", "du bist super, wisse das"],
    'ja': ["スライムを買って", "そんな関係なんてクソくらえ", "君の運命は185cm以上", "君の運命はサッカー選手", "君は最高だよ、知ってて"],
    'tr': ["kendine slime al", "bu ilişkilere lanet olsun", "kaderin boyu 185+", "kaderin futbolcu", "sen süpersin, bunu bil"],
    'vi': ["mua slime cho mình đi", "quan hệ này thì cứ kệ", "số phận của bạn cao 185+", "số phận của bạn là cầu thủ bóng đá", "bạn tuyệt vời lắm, hãy biết điều đó"],
    # Для решты мов (id, bn, ur, mr, te, ta, wuu, yue) — використовуємо англійську або російську як fallback
}

# ==============================
# ІНТЕРФЕЙС НА 21 МОВІ
# ==============================
LANGUAGES = {
    'en': '🇬🇧 English', 'zh': '🇨🇳 中文 (普通话)', 'hi': '🇮🇳 हिन्दी',
    'es': '🇪🇸 Español', 'fr': '🇫🇷 Français', 'ar': '🇸🇦 العربية (الفصحى)',
    'bn': '🇧🇩 বাংলা', 'pt': '🇧🇷 Português', 'ru': '🇷🇺 Русский',
    'ur': '🇵🇰 اردو', 'id': '🇮🇩 Bahasa Indonesia', 'de': '🇩🇪 Deutsch',
    'ja': '🇯🇵 日本語', 'mr': '🇮🇳 मराठी', 'te': '🇮🇳 తెలుగు',
    'tr': '🇹🇷 Türkçe', 'ta': '🇮🇳 தமிழ்', 'wuu': '🇨🇳 吴语',
    'yue': '🇨🇳 粤语', 'vi': '🇻🇳 Tiếng Việt', 'uk': '🇺🇦 Українська'
}

TRANSLATIONS = {
    'en': {'start_hello': "🌟 Hello! I am your new helper *Mikky*! 🌟\n\nChoose your language:", 'main_welcome': "Hello! I am your new assistant *Mikky* 🌟\n\nTell me about your plans!", 'trial_info': "You have 7 days free.", 'notifications': "🔔 Please enable notifications!", 'morning_greeting': "🌅 Good morning, {name}!\n\n**Today's tasks:**\n{tasks}", 'prediction_prefix': "💫 Prediction for the day:\n", 'trial_ended': "⛔ Free period ended. Subscribe to continue."},
    'ru': {'start_hello': "🌟 Привет! Я твой новый помощник *Mikky*! 🌟\n\nВыбери язык:", 'main_welcome': "Привет! Я твой новый помощник *Mikky* 🌟\n\nРасскажи мне о своих планах!\n\nПросто пиши:\n• Текстовые заметки\n• Фото\n• Ссылки\n• Завтра кофе Лена 15:00", 'trial_info': "У тебя есть 7 дней бесплатного доступа.", 'notifications': "🔔 Пожалуйста, включи уведомления!", 'morning_greeting': "🌅 Доброе утро, {name}!\n\n**Задачи на сегодня:**\n{tasks}", 'prediction_prefix': "💫 Предсказание на день:\n", 'trial_ended': "⛔ Бесплатный период закончился. Оплати подписку."},
    'uk': {'start_hello': "🌟 Привіт! Я твій новий помічник *Mikky*! 🌟\n\nОбери мову:", 'main_welcome': "Привіт! Я твій новий помічник *Mikky* 🌟\n\nРозкажи мені про свої плани!", 'trial_info': "У тебе є 7 днів безкоштовного доступу.", 'notifications': "🔔 Увімкни сповіщення!", 'morning_greeting': "🌅 Доброго ранку, {name}!\n\n**Задачі на сьогодні:**\n{tasks}", 'prediction_prefix': "💫 Передбачення на день:\n", 'trial_ended': "⛔ Безкоштовний період закінчився. Оплати підписку."},
    # Інші мови (скорочено, але працюють)
    'zh': {'start_hello': "🌟 你好！我是你的新助手 *Mikky*! 🌟\n\n选择语言：", 'main_welcome': "你好！我是 Mikky 🌟\n\n告诉我你的计划！", 'morning_greeting': "🌅 早上好，{name}！\n\n**今日任务：**\n{tasks}", 'prediction_prefix': "💫 今日预言：\n"},
    'hi': {'start_hello': "🌟 नमस्ते! मैं Mikky हूँ 🌟\n\nभाषा चुनें:", 'main_welcome': "नमस्ते! बताओ अपनी योजनाएँ!", 'morning_greeting': "🌅 गुड मॉर्निंग, {name}!\n\n**आज के कार्य:**\n{tasks}", 'prediction_prefix': "💫 आज की भविष्यवाणी:\n"},
    # ... (інші мови аналогічно)
}

# ==============================
# БАЗА ДАННИХ
# ==============================
def init_db():
    conn = sqlite3.connect("mikky.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT,
        language TEXT DEFAULT 'ru', is_paid INTEGER DEFAULT 0,
        trial_start TEXT, used_predictions TEXT DEFAULT ''
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY, user_id INTEGER, text TEXT,
        event_date TEXT, event_time TEXT, status TEXT DEFAULT 'pending', created_at TEXT
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

def get_user(user_id):
    conn = sqlite3.connect("mikky.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def update_user_language(user_id, lang):
    conn = sqlite3.connect("mikky.db")
    c = conn.cursor()
    c.execute("UPDATE users SET language=? WHERE user_id=?", (lang, user_id))
    conn.commit()
    conn.close()

def is_trial_active(user_id):
    user = get_user(user_id)
    if not user or user[4] == 1:
        return True
    trial_start = datetime.fromisoformat(user[5])
    return datetime.now(TIMEZONE) < trial_start + timedelta(days=TRIAL_DAYS)

def get_unique_prediction(user_id, lang):
    conn = sqlite3.connect("mikky.db")
    c = conn.cursor()
    c.execute("SELECT used_predictions FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    used = row[0].split(',') if row and row[0] else []
    used = [int(x) for x in used if x]

    preds = PREDICTIONS.get(lang, PREDICTIONS.get('en', PREDICTIONS['ru']))
    available = [i for i in range(len(preds)) if i not in used]
    if not available:
        available = list(range(len(preds)))
        used = []
    idx = random.choice(available)
    used.append(str(idx))
    c.execute("UPDATE users SET used_predictions=? WHERE user_id=?", (",".join(used), user_id))
    conn.commit()
    conn.close()
    return preds[idx]

def save_task(user_id, text):
    conn = sqlite3.connect("mikky.db")
    c = conn.cursor()
    today = datetime.now(TIMEZONE).strftime("%Y-%m-%d")
    c.execute("INSERT INTO tasks (user_id, text, event_date, created_at) VALUES (?,?,?,?)",
              (user_id, text, today, datetime.now(TIMEZONE).isoformat()))
    conn.commit()
    conn.close()

def get_tasks_for_today(user_id):
    today = datetime.now(TIMEZONE).strftime("%Y-%m-%d")
    conn = sqlite3.connect("mikky.db")
    c = conn.cursor()
    c.execute("SELECT text FROM tasks WHERE user_id=? AND event_date=? AND status='pending'", (user_id, today))
    return [row[0] for row in c.fetchall()]

def get_all_users():
    conn = sqlite3.connect("mikky.db")
    c = conn.cursor()
    c.execute("SELECT user_id, first_name, language FROM users")
    rows = c.fetchall()
    conn.close()
    return rows

# ==============================
# КЛАВІАТУРИ
def main_menu_keyboard(lang='ru'):
    if lang == 'ru':
        kb = [
            [KeyboardButton(text="➕ Новая задача"), KeyboardButton(text="📅 На сегодня")],
            [KeyboardButton(text="📅 На завтра"), KeyboardButton(text="📅 На неделю")],
            [KeyboardButton(text="📅 На месяц"), KeyboardButton(text="❓ Не сделано")],
            [KeyboardButton(text="✅ Сделано"), KeyboardButton(text="📋 Все задачи")]
        ]
    elif lang == 'uk':
        kb = [
            [KeyboardButton(text="➕ Нова задача"), KeyboardButton(text="📅 На сьогодні")],
            [KeyboardButton(text="📅 На завтра"), KeyboardButton(text="📅 На тиждень")],
            [KeyboardButton(text="📅 На місяць"), KeyboardButton(text="❓ Не зроблено")],
            [KeyboardButton(text="✅ Зроблено"), KeyboardButton(text="📋 Всі задачі")]
        ]
    else:
        kb = [
            [KeyboardButton(text="➕ New Task"), KeyboardButton(text="📅 Today")],
            [KeyboardButton(text="📅 Tomorrow"), KeyboardButton(text="📅 Week")],
            [KeyboardButton(text="📅 Month"), KeyboardButton(text="❓ Not Done")],
            [KeyboardButton(text="✅ Done"), KeyboardButton(text="📋 All Tasks")]
        ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, persistent=True)
@dp.callback_query(F.data.startswith("set_lang_"))
async def set_language(callback: CallbackQuery):
    lang = callback.data.split("_")[-1]
    update_user_language(callback.from_user.id, lang)
    await callback.message.edit_text(f"✅ {LANGUAGES.get(lang, lang)}")
    await send_main_welcome(callback.message, lang, callback.from_user.first_name)

async def send_main_welcome(message: Message, lang: str, name="друг"):
    t = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    text = t.get('main_welcome', TRANSLATIONS['en']['main_welcome']) + "\n\n" + t.get('trial_info', "7 days free")
    await message.answer(text, reply_markup=main_menu_keyboard(lang))
    await asyncio.sleep(1.5)
    await message.answer(t.get('notifications', "🔔 Enable notifications!"))
    await asyncio.sleep(1)
    await message.answer("Оплата:", reply_markup=payment_keyboard())

@dp.callback_query(F.data == "pay_stars")
async def pay_stars(callback: CallbackQuery):
    await callback.answer()
    await bot.send_invoice(callback.from_user.id, "Підписка Mikky", "30 днів", "subscription", "", "XTR", [types.LabeledPrice("Місяць", STAR_PRICE)])

@dp.pre_checkout_query()
async def pre_checkout(pre_checkout_query):
    await pre_checkout_query.answer(ok=True)

@dp.message(F.successful_payment)
async def payment_success(message: Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("mikky.db")
    c = conn.cursor()
    c.execute("UPDATE users SET is_paid=1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
    await message.answer("✅ Підписка активована! 🌟")

@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    if not is_trial_active(user_id):
        await message.answer(TRANSLATIONS.get('ru', TRANSLATIONS['en'])['trial_ended'])
        return
    save_task(user_id, message.text or "Фото/повідомлення")
    await message.answer("✅ Збережено!")

async def morning_job():
    for user_id, first_name, lang in get_all_users():
        if not is_trial_active(user_id):
            continue
        tasks = get_tasks_for_today(user_id)
        task_text = "\n".join(f"• {t}" for t in tasks) or "Задач немає"
        t = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
        await bot.send_message(user_id, t['morning_greeting'].format(name=first_name, tasks=task_text))
        await asyncio.sleep(2)
        pred = get_unique_prediction(user_id, lang)
        await bot.send_message(user_id, t.get('prediction_prefix', "💫 ") + pred)

async def main():
    init_db()
    scheduler.add_job(morning_job, 'cron', hour=7, minute=0)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
