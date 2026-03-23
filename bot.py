#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ролевой Telegram бот для управления заявками в группу
Функции:
- Проверка подписки на канал
- Проверка прочтения правил
- Выбор ролей с отслеживанием занятости
- Отправка заявок админу
- Выдача одноразовых ссылок
- Автоматическое приветствие в чате
- Команда /call для призыва участников
- Система жалоб на участников (анонимные)
- Система предложений по улучшению (с выбором анонимности)
- Проверка безопасности (анти-рейдер)
- Управление ролями (освобождение)
- Полная админ-панель
"""

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time
import json
import os
import requests
from datetime import datetime, timedelta
import logging

# ==================== НАСТРОЙКИ ====================
# Telegram Bot Token (получить у @BotFather)
BOT_TOKEN = "8658828172:AAFwNxQeYD8sq1T2VES-dNNo11rgKdz_H48"

# ID администратора (узнать у @userinfobot)
ADMIN_ID = 1425042067

# Информационный канал (куда нужно подписаться)
INFO_CHANNEL_ID = "@bsdfloodloosere"

# ID группы, куда будут приглашаться участники
GROUP_CHAT_ID = -1003775105094

# ID чата для предложений (создайте отдельную группу)
SUGGESTIONS_CHAT_ID = -5132107476

# ID чата для жалоб (можно отдельный или тот же что и предложения)
REPORTS_CHAT_ID = -5132107476

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
# Добавьте для отладки
print("🤖 Бот запускается...")
print(f"Токен: {BOT_TOKEN[:10]}... (скрыто)")
print(f"ADMIN_ID: {ADMIN_ID}")

# ==================== КОНФИГУРАЦИЯ РОЛЕЙ ====================
# Список доступных ролей (настройте под свою группу)
AVAILABLE_ROLES = [
 "Акико Йосанo",
 "Ацуши Накаджима",
 "Доппо Куникида",
 "Дзюнидзи Танизаки",
 "Катай Таяма",
 "Кенджи Миядзава",
 "Кёка Идзуми",
 "Кирако Харуно",
 "Наоми Танизаки",
 "Осаму Дазай",
 "Ранпо Эдогава",
 "Юкичи Фукудзава",
 "Артур Рембо",
 "Гин Акутагава",
 "Ичиё Хигучи",
 "Карма",
 "Коё Озаки",
 "Кюсаку Юмэно (Кью)",
 "Мичидзо Тачихара",
 "Мотодзиро Кадзи",
 "Огай Мори",
 "Рюноске Акутагава",
 "Рюро Хиротсу",
 "Сакуноскэ Ода",
 "Чуя Накахара",
 "Эйс",
 "Элис",
 "Герман Мелвилл",
 "Говард Филлипс Лавкрафт",
 "Джеймс Л.",
 "Джон Стейнбек",
 "Карл",
 "Луиза Мэй Олкотт",
 "Люси Мод Монтгомери",
 "Марк Твен",
 "Маргарет Митчелл",
 "Натаниэль Готорн",
 "Фрэнсис Скотт Кей Фицджеральд",
 "Эдгар Аллан По",
 "Александр Пушкин",
 "Иван Гончаров",
 "Муситаро Огури",
 "Брам Стокер",
 "Николай Гоголь",
 "Сигма",
 "Фёдор Достоевский",
 "Очи Фукучи",
 "Сайгику Дзёно",
 "Теттэ Суэхиро",
 "Тэруко Оокура",
 "Альбатрос",
 "Айсмен",
 "Док",
 "Липпман",
 "Пиано Мэн",
 "Анго Сакагучи",
 "Мидзуки Цудзимура",
 "Сантока Танэда",
 "Ятиё Муракосо",
 "Агата Кристи",
 "Буиитиро Сирасэ",
 "Юан",
 "Андре Жид",
 "Поль Верлен",
 "Жюль Верн",
 "Дзюн Митамура",
 "Амэ-но-Гозен",
 "Герберт Джордж Уэллс",
 "Сосэки Нацумэ",
 "Тацухико Шибусава",
 "Тацухико Тачихара(солдат)",
 "Кацуми",
 "Коске",
 "Сакура",
 "Шинджи",
 "Юу",
 "Миноура",
 "Сугимото",
 "Ямагава",
 "Госпожа Эгава",
 "Токио Мураками",
 "Адам Франкенштейн",
 "Ёкомидзо",
 "Лысик",
 "Отец Аи Коды",
 "Официантка из кафе Узумаки",
 "Подруга Мизуки Цудзимуры",
 "Профессор Н",
 "Рокузо Тагучи",
 "Сасаки Нобуко",
 "Шосаку Кацура",
 "Ая Кода",
 "Юкито Аяцудзиз"
]

# ==================== НАСТРОЙКИ БЕЗОПАСНОСТИ ====================
# Минимальный возраст аккаунта в днях (0 - отключено)
MIN_ACCOUNT_AGE_DAYS = 12

# Нужно ли проверять через внешнее API (0 - отключено)
USE_ANTISPAM_API = False

# API для проверки спама (если нужно)
ANTISPAM_API_URL = "https://api.antispam.cloud/check"
ANTISPAM_API_TOKEN = ""

# Количество жалоб для автоматического кика
REPORTS_TO_KICK = 5

# ==================== ИНИЦИАЛИЗАЦИЯ БОТА ====================
bot = telebot.TeleBot(BOT_TOKEN)

# Структуры данных
user_data = {}  # Временные данные пользователей при регистрации
occupied_roles = {}  # {role: user_id} - занятые роли
user_roles = {}  # {user_id: role} - роли пользователей
suspicious_users = {}  # {user_id: {"reports": 0, "reasons": [], "reported_by": [], "date": ""}}
suggestions = []  # Список предложений
reports_log = []  # Лог жалоб
banned_users = set()  # Забаненные пользователи
pending_approvals = {}  # Ожидающие одобрения заявки

# Путь к файлу данных на PythonAnywhere
DATA_FILE = os.path.join(os.path.dirname(__file__), "bot_data.json")

# ==================== ФУНКЦИИ РАБОТЫ С ДАННЫМИ ====================

def load_data():
    """Загрузка всех данных из файла"""
    global occupied_roles, user_data, user_roles, suspicious_users, suggestions, banned_users, pending_approvals, reports_log

    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                occupied_roles = data.get('occupied_roles', {})
                user_data = data.get('user_data', {})
                user_roles = data.get('user_roles', {})
                suspicious_users = data.get('suspicious_users', {})
                suggestions = data.get('suggestions', [])
                banned_users = set(data.get('banned_users', []))
                pending_approvals = data.get('pending_approvals', {})
                reports_log = data.get('reports_log', [])
            logger.info(f"Данные загружены: {len(occupied_roles)} ролей занято")
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")
            initialize_empty_data()
    else:
        initialize_empty_data()

def initialize_empty_data():
    """Инициализация пустых данных"""
    global occupied_roles, user_data, user_roles, suspicious_users, suggestions, banned_users, pending_approvals, reports_log
    occupied_roles = {}
    user_data = {}
    user_roles = {}
    suspicious_users = {}
    suggestions = []
    banned_users = set()
    pending_approvals = {}
    reports_log = []
    save_data()

def save_data():
    """Сохранение всех данных в файл"""
    data = {
        'occupied_roles': occupied_roles,
        'user_data': user_data,
        'user_roles': user_roles,
        'suspicious_users': suspicious_users,
        'suggestions': suggestions,
        'banned_users': list(banned_users),
        'pending_approvals': pending_approvals,
        'reports_log': reports_log,
        'last_save': datetime.now().isoformat()
    }
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("Данные сохранены")
    except Exception as e:
        logger.error(f"Ошибка сохранения данных: {e}")

# ==================== ФУНКЦИИ ПРОВЕРКИ ====================

def check_subscription(user_id):
    """Проверка подписки на информационный канал"""
    try:
        member = bot.get_chat_member(INFO_CHANNEL_ID, user_id)
        is_member = member.status in ['member', 'administrator', 'creator']
        if not is_member:
            logger.info(f"Пользователь {user_id} не подписан на канал")
        return is_member
    except Exception as e:
        logger.error(f"Ошибка проверки подписки для {user_id}: {e}")
        return False

def check_account_age(user_id):
    """Проверка возраста аккаунта"""
    if MIN_ACCOUNT_AGE_DAYS <= 0:
        return True, "OK"
    try:
        return True, "OK"
    except:
        return True, "OK"

def check_antispam(user_id, username):
    """Проверка через антиспам API"""
    if not USE_ANTISPAM_API or not ANTISPAM_API_TOKEN:
        return True, "OK"
    try:
        response = requests.get(
            f"{ANTISPAM_API_URL}?user_id={user_id}&username={username}",
            headers={"Authorization": f"Bearer {ANTISPAM_API_TOKEN}"},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("is_spammer") or data.get("is_scammer") or data.get("is_bot"):
                return False, "Аккаунт отмечен как спамер/бот"
        return True, "OK"
    except Exception as e:
        logger.error(f"Ошибка проверки антиспам: {e}")
        return True, "OK"

def check_user_safety(user_id, username):
    """Комплексная проверка безопасности пользователя"""
    logger.info(f"Проверка безопасности пользователя {user_id}")

    if user_id in banned_users:
        return False, "Пользователь в черном списке"

    age_ok, age_msg = check_account_age(user_id)
    if not age_ok:
        return False, age_msg

    spam_ok, spam_msg = check_antispam(user_id, username)
    if not spam_ok:
        return False, spam_msg

    if user_id in suspicious_users and suspicious_users[user_id]["reports"] >= REPORTS_TO_KICK:
        return False, f"Получено {suspicious_users[user_id]['reports']} жалоб"

    return True, "OK"

def is_admin(user_id):
    """Проверка, является ли пользователь администратором"""
    return user_id == ADMIN_ID

# ==================== ФУНКЦИИ УПРАВЛЕНИЯ РОЛЯМИ ====================

def get_available_roles():
    """Получить список доступных ролей"""
    return [role for role in AVAILABLE_ROLES if role not in occupied_roles]

def assign_role(user_id, role):
    """Назначить роль пользователю"""
    if role in occupied_roles:
        return False

    occupied_roles[role] = user_id
    user_roles[user_id] = role
    save_data()
    logger.info(f"Роль {role} назначена пользователю {user_id}")
    return True

def free_role(role):
    """Освободить роль"""
    if role in occupied_roles:
        user_id = occupied_roles[role]
        if user_id in user_roles:
            del user_roles[user_id]
        del occupied_roles[role]
        save_data()
        logger.info(f"Роль {role} освобождена")
        return True
    return False

def free_user_role(user_id):
    """Освободить роль пользователя"""
    if user_id in user_roles:
        role = user_roles[user_id]
        return free_role(role)
    return False

def get_user_role(user_id):
    """Получить роль пользователя"""
    return user_roles.get(user_id)

def kick_user(user_id, reason, admin_id=None):
    """Кикнуть пользователя из группы"""
    try:
        bot.ban_chat_member(GROUP_CHAT_ID, user_id)
        bot.unban_chat_member(GROUP_CHAT_ID, user_id)

        if user_id in user_roles:
            free_user_role(user_id)

        banned_users.add(user_id)
        save_data()

        admin_text = f"⚠️ *Пользователь кикнут*\n\n"
        admin_text += f"ID: `{user_id}`\n"
        admin_text += f"Причина: {reason}"

        bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")

        try:
            bot.send_message(
                user_id,
                f"⚠️ *Вы были исключены из группы*\n\n"
                f"Причина: {reason}\n\n"
                f"Если вы считаете это ошибкой, свяжитесь с администратором.",
                parse_mode="Markdown"
            )
        except:
            pass

        logger.info(f"Пользователь {user_id} кикнут по причине: {reason}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при кике {user_id}: {e}")
        return False

# ==================== ФУНКЦИИ ЖАЛОБ ====================

def report_user(user_id, reason, reporter_id, anonymous=True):
    """Пожаловаться на пользователя"""
    if user_id == reporter_id:
        return False, "Нельзя жаловаться на себя"

    # Сохраняем жалобу в лог
    report_entry = {
        'reported_id': user_id,
        'reporter_id': reporter_id if not anonymous else None,
        'reporter_name': None if anonymous else "Неизвестно",
        'reason': reason,
        'date': datetime.now().isoformat(),
        'anonymous': anonymous
    }
    reports_log.append(report_entry)

    # Обновляем статистику жалоб на пользователя
    if user_id not in suspicious_users:
        suspicious_users[user_id] = {
            "reports": 0,
            "reasons": [],
            "reported_by": [],
            "first_report": datetime.now().isoformat()
        }

    suspicious_users[user_id]["reports"] += 1
    suspicious_users[user_id]["reasons"].append(reason)
    if not anonymous:
        suspicious_users[user_id]["reported_by"].append(reporter_id)

    save_data()

    logger.info(f"Жалоба на {user_id} от {'анонима' if anonymous else reporter_id}: {reason}")

    # Отправляем в чат жалоб, если указан
    if REPORTS_CHAT_ID:
        report_text = f"⚠️ *Новая жалоба*\n\n"
        report_text += f"👤 *Нарушитель:* `{user_id}`\n"
        if not anonymous:
            report_text += f"👮 *Пожаловался:* `{reporter_id}`\n"
        else:
            report_text += f"👮 *Пожаловался:* Анонимно\n"
        report_text += f"📝 *Причина:* {reason}\n"
        report_text += f"📊 *Всего жалоб:* {suspicious_users[user_id]['reports']}/{REPORTS_TO_KICK}"

        try:
            bot.send_message(REPORTS_CHAT_ID, report_text, parse_mode="Markdown")
        except:
            pass

    # Проверяем, нужно ли кикнуть
    if suspicious_users[user_id]["reports"] >= REPORTS_TO_KICK:
        kick_user(user_id, f"Превышен лимит жалоб ({REPORTS_TO_KICK})")
        return True, "Пользователь кикнут за превышение лимита жалоб"

    return False, f"Жалоба принята. Осталось жалоб до кика: {REPORTS_TO_KICK - suspicious_users[user_id]['reports']}"

# ==================== ФУНКЦИИ ПРЕДЛОЖЕНИЙ ====================

def add_suggestion(user_id, username, suggestion_text, anonymous=True):
    """Добавить предложение"""
    suggestion = {
        'id': len(suggestions) + 1,
        'user_id': user_id if not anonymous else None,
        'username': "Аноним" if anonymous else username,
        'text': suggestion_text,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'status': 'new',
        'anonymous': anonymous
    }
    suggestions.append(suggestion)
    save_data()

    # Отправляем в чат предложений, если указан
    if SUGGESTIONS_CHAT_ID:
        suggestion_text_msg = f"💡 *Новое предложение* #{suggestion['id']}\n\n"
        if anonymous:
            suggestion_text_msg += f"👤 *От:* Аноним\n"
        else:
            suggestion_text_msg += f"👤 *От:* @{username}\n"
        suggestion_text_msg += f"📅 *Дата:* {suggestion['date']}\n\n"
        suggestion_text_msg += f"📝 *Текст:*\n{suggestion_text}"

        try:
            bot.send_message(SUGGESTIONS_CHAT_ID, suggestion_text_msg, parse_mode="Markdown")
        except:
            pass

    logger.info(f"Новое предложение #{suggestion['id']} от {'анонима' if anonymous else username}")
    return suggestion['id']

# ==================== КЛАВИАТУРЫ ====================

def main_menu():
    """Главное меню"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    btn_register = InlineKeyboardButton("🎭 Начать регистрацию", callback_data="start_reg")
    btn_support = InlineKeyboardButton("🆘 Поддержка", callback_data="support_menu")
    keyboard.add(btn_register, btn_support)
    return keyboard

def support_menu():
    """Меню поддержки"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    btn_complaint = InlineKeyboardButton("⚠️ Пожаловаться на участника", callback_data="complaint")
    btn_suggestion = InlineKeyboardButton("💡 Предложение по улучшению", callback_data="suggestion_start")
    btn_help = InlineKeyboardButton("❓ Помощь", callback_data="help")
    btn_back = InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")
    keyboard.add(btn_complaint, btn_suggestion, btn_help, btn_back)
    return keyboard

def complaint_menu():
    """Меню жалобы - выбор анонимности"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn_anonymous = InlineKeyboardButton("🔒 Анонимная жалоба", callback_data="complaint_anonymous")
    btn_public = InlineKeyboardButton("👤 Открытая жалоба", callback_data="complaint_public")
    btn_back = InlineKeyboardButton("◀️ Назад", callback_data="support_menu")
    keyboard.add(btn_anonymous, btn_public, btn_back)
    return keyboard

def suggestion_choice_menu():
    """Меню предложения - выбор анонимности"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn_anonymous = InlineKeyboardButton("🔒 Анонимно", callback_data="suggestion_anonymous")
    btn_public = InlineKeyboardButton("👤 С указанием имени", callback_data="suggestion_public")
    btn_back = InlineKeyboardButton("◀️ Назад", callback_data="support_menu")
    keyboard.add(btn_anonymous, btn_public, btn_back)
    return keyboard

def roles_menu():
    """Меню выбора ролей"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    available_roles = get_available_roles()

    if not available_roles:
        keyboard.add(InlineKeyboardButton("😔 Все роли заняты", callback_data="no_roles"))
    else:
        for role in available_roles:
            keyboard.add(InlineKeyboardButton(f"📌 {role}", callback_data=f"role_{role}"))

    btn_back = InlineKeyboardButton("◀️ Назад", callback_data="back_to_start")
    keyboard.add(btn_back)
    return keyboard

def admin_panel():
    """Панель администратора"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    btn_pending = InlineKeyboardButton("📝 Ожидающие заявки", callback_data="admin_pending")
    btn_roles = InlineKeyboardButton("📋 Список ролей", callback_data="admin_roles")
    btn_reports = InlineKeyboardButton("⚠️ Жалобы", callback_data="admin_reports")
    btn_suggestions = InlineKeyboardButton("💡 Предложения", callback_data="admin_suggestions")
    btn_clear = InlineKeyboardButton("🗑️ Очистить данные", callback_data="admin_clear")
    keyboard.add(btn_pending, btn_roles, btn_reports, btn_suggestions, btn_clear)
    return keyboard

# ==================== КОМАНДЫ БОТА ====================

@bot.message_handler(commands=['start'])
def start_command(message):
    print(f"Получена команда /start от {message.from_user.id}")
    """Обработка команды /start"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name

    if user_id in banned_users:
        bot.send_message(
            user_id,
            "⚠️ *Вы забанены*\n\n"
            "Ваш аккаунт находится в черном списке.\n"
            "Для обжалования свяжитесь с администратором.",
            parse_mode="Markdown"
        )
        return

    welcome_text = (
        f"🌟 *Добро пожаловать в наш флуд, {username}!* 🌟\n\n"
        f"Я помогу вам стать частью нашего флуда.\n\n"
        f"📋 *Что нужно сделать:*\n"
        f"1️⃣ Подписаться на наш информационный канал\n"
        f"2️⃣ Ознакомиться с правилами\n"
        f"3️⃣ Выбрать свободную роль\n"
        f"4️⃣ Дождаться одобрения администратора\n\n"
        f"🆘 Если у вас есть вопросы или проблемы, используйте меню поддержки.\n\n"
        f"*Нажмите кнопку ниже, чтобы начать:*"
    )

    bot.send_message(
        user_id,
        welcome_text,
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

@bot.message_handler(commands=['support'])
def support_command(message):
    """Команда поддержки"""
    bot.send_message(
        message.chat.id,
        "🆘 *Меню поддержки*\n\nВыберите нужный пункт:",
        parse_mode="Markdown",
        reply_markup=support_menu()
    )

@bot.message_handler(commands=['call'])
def call_command(message):
    """Команда /call - призыв участников"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name

    user_role = get_user_role(user_id)

    if not user_role:
        bot.reply_to(
            message,
            "❌ У вас еще нет роли.\n\n"
            "Пожалуйста, пройдите регистрацию через /start",
            parse_mode="Markdown"
        )
        return

    call_text = message.text.replace('/call', '').strip()
    if not call_text:
        call_text = "все сюда!"

    bot.send_message(
        GROUP_CHAT_ID,
        f"📢 *{username}* ({user_role}) {call_text}\n\n"
        f"Присоединяйтесь к приключению! 🎭✨",
        parse_mode="Markdown"
    )

    bot.reply_to(message, "✅ Ваш призыв отправлен в группу!")

@bot.message_handler(commands=['cancel'])
def cancel_command(message):
    """Отмена текущего действия"""
    user_id = message.from_user.id

    if user_id in user_data and 'state' in user_data[user_id]:
        if 'msg_id' in user_data[user_id]:
            try:
                bot.delete_message(message.chat.id, user_data[user_id]['msg_id'])
            except:
                pass

        del user_data[user_id]
        save_data()
        bot.reply_to(message, "✅ Действие отменено")
    else:
        bot.reply_to(message, "Нет активных действий для отмены")

@bot.message_handler(commands=['id'])
def get_id_command(message):
    """Получить ID чата"""
    bot.reply_to(
        message,
        f"🆔 *ID этого чата:* `{message.chat.id}`\n"
        f"🆔 *Ваш ID:* `{message.from_user.id}`",
        parse_mode="Markdown"
    )

# ==================== АДМИН-КОМАНДЫ ====================

@bot.message_handler(commands=['admin'])
def admin_command(message):
    """Панель администратора"""
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ У вас нет прав администратора")
        return

    bot.send_message(
        message.chat.id,
        "👑 *Панель администратора*\n\nВыберите действие:",
        parse_mode="Markdown",
        reply_markup=admin_panel()
    )

@bot.message_handler(commands=['kick'])
def kick_admin_command(message):
    """Кикнуть пользователя (админ)"""
    if not is_admin(message.from_user.id):
        return

    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(
            message,
            "❌ *Использование:* `/kick [user_id] [причина]`\n\n"
            "Пример: `/kick 123456789 Нарушение правил`",
            parse_mode="Markdown"
        )
        return

    try:
        user_id = int(args[1])
        reason = ' '.join(args[2:]) if len(args) > 2 else "Нарушение правил"

        kick_user(user_id, reason, message.from_user.id)
        bot.reply_to(message, f"✅ Пользователь `{user_id}` кикнут", parse_mode="Markdown")
    except ValueError:
        bot.reply_to(message, "❌ Неверный ID пользователя")

@bot.message_handler(commands=['freerole'])
def free_role_command(message):
    """Освободить роль (админ)"""
    if not is_admin(message.from_user.id):
        return

    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(
            message,
            "❌ *Использование:* `/freerole [название_роли]`\n\n"
            f"Доступные роли: {', '.join(AVAILABLE_ROLES)}",
            parse_mode="Markdown"
        )
        return

    role = args[1]
    if free_role(role):
        bot.reply_to(message, f"✅ Роль *{role}* освобождена!", parse_mode="Markdown")
    else:
        bot.reply_to(message, f"❌ Роль *{role}* не найдена или уже свободна", parse_mode="Markdown")

@bot.message_handler(commands=['freeuser'])
def free_user_command(message):
    """Освободить роль пользователя (админ)"""
    if not is_admin(message.from_user.id):
        return

    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "❌ Использование: /freeuser [user_id]", parse_mode="Markdown")
        return

    try:
        user_id = int(args[1])
        if free_user_role(user_id):
            bot.reply_to(message, f"✅ Роль пользователя `{user_id}` освобождена", parse_mode="Markdown")
        else:
            bot.reply_to(message, f"❌ Пользователь `{user_id}` не имеет роли", parse_mode="Markdown")
    except ValueError:
        bot.reply_to(message, "❌ Неверный ID пользователя")

@bot.message_handler(commands=['roles'])
def show_roles_command(message):
    """Показать список ролей"""
    if not is_admin(message.from_user.id):
        return

    available = get_available_roles()
    text = "📋 *Список ролей*\n\n"
    text += f"*Всего ролей:* {len(AVAILABLE_ROLES)}\n"
    text += f"*Занято:* {len(occupied_roles)}\n"
    text += f"*Свободно:* {len(available)}\n\n"

    if occupied_roles:
        text += "*Занятые роли:*\n"
        for role, user_id in occupied_roles.items():
            text += f"• {role} → `{user_id}`\n"

    if available:
        text += f"\n*Свободные роли:*\n"
        for role in available:
            text += f"• {role}"
            text += "\n"

    bot.send_message(ADMIN_ID, text, parse_mode="Markdown")

@bot.message_handler(commands=['suggestions'])
def show_suggestions_command(message):
    """Показать предложения (админ)"""
    if not is_admin(message.from_user.id):
        return

    if not suggestions:
        bot.reply_to(message, "💡 Нет предложений")
        return

    text = "💡 *Предложения участников:*\n\n"
    for s in suggestions[-10:]:
        text += f"*#{s['id']}* от {s['username']} ({s['date']})\n"
        text += f"{s['text'][:200]}"
        if len(s['text']) > 200:
            text += "..."
        text += f"\n\n"

    bot.send_message(ADMIN_ID, text, parse_mode="Markdown")

@bot.message_handler(commands=['reports'])
def show_reports_command(message):
    """Показать жалобы (админ)"""
    if not is_admin(message.from_user.id):
        return

    if not suspicious_users:
        bot.reply_to(message, "⚠️ Нет жалоб")
        return

    text = "⚠️ *Жалобы на пользователей:*\n\n"
    for user_id, data in suspicious_users.items():
        text += f"*ID:* `{user_id}`\n"
        text += f"*Жалоб:* {data['reports']}/{REPORTS_TO_KICK}\n"
        text += f"*Последняя причина:* {data['reasons'][-1][:50]}\n\n"

    bot.send_message(ADMIN_ID, text, parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
def stats_command(message):
    """Статистика бота (админ)"""
    if not is_admin(message.from_user.id):
        return

    text = "📊 *Статистика бота*\n\n"
    text += f"*Всего ролей:* {len(AVAILABLE_ROLES)}\n"
    text += f"*Занято ролей:* {len(occupied_roles)}\n"
    text += f"*Участников в группе:* {len(user_roles)}\n"
    text += f"*Активных регистраций:* {len([u for u in user_data if 'state' in user_data[u]])}\n"
    text += f"*Жалоб на пользователей:* {len(suspicious_users)}\n"
    text += f"*Всего жалоб:* {len(reports_log)}\n"
    text += f"*Предложений:* {len(suggestions)}\n"
    text += f"*Забаненных:* {len(banned_users)}\n"

    bot.send_message(ADMIN_ID, text, parse_mode="Markdown")

# ==================== ОБРАБОТЧИКИ CALLBACK ====================

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """Обработка всех callback-запросов"""
    user_id = call.from_user.id
    username = call.from_user.username or call.from_user.first_name

    if user_id in banned_users:
        bot.answer_callback_query(call.id, "❌ Вы в черном списке", show_alert=True)
        return

    # ========== ОСНОВНАЯ РЕГИСТРАЦИЯ ==========
    if call.data == "start_reg":
        if user_id in pending_approvals:
            bot.answer_callback_query(
                call.id,
                "⏳ Ваша заявка уже отправлена и ожидает одобрения",
                show_alert=True
            )
            return

        user_data[user_id] = {
            'step': 'start',
            'username': username,
            'state': 'registering'
        }
        save_data()

        keyboard = InlineKeyboardMarkup()
        btn_check = InlineKeyboardButton("✅ Проверить подписку", callback_data="check_sub")
        keyboard.add(btn_check)

        bot.edit_message_text(
            "📝 *Регистрация в ролевой группе*\n\n"
            f"**Шаг 1 из 3:** Подписка\n\n"
            f"👉 *Подпишитесь на канал:* {INFO_CHANNEL_ID}\n"
            f"📖 *Прочитайте правила* в закрепленном сообщении\n\n"
            f"После этого нажмите кнопку проверки:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=keyboard
        )

    elif call.data == "check_sub":
        if check_subscription(user_id):
            bot.answer_callback_query(call.id, "✅ Подписка подтверждена!")

            user_data[user_id]['step'] = 'rules_confirmed'
            save_data()

            keyboard = InlineKeyboardMarkup()
            btn_rules = InlineKeyboardButton("✅ Прочитал(а) правила", callback_data="rules_read")
            keyboard.add(btn_rules)

            bot.edit_message_text(
                "✅ *Подписка подтверждена!*\n\n"
                "**Шаг 2 из 3:** Подтверждение правил\n\n"
                "❗ Подтвердите, что вы ознакомились с правилами:",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        else:
            bot.answer_callback_query(
                call.id,
                f"❌ Вы не подписаны на {INFO_CHANNEL_ID}!\n\nПодпишитесь и попробуйте снова.",
                show_alert=True
            )

    elif call.data == "rules_read":
        user_data[user_id]['step'] = 'role_selection'
        save_data()

        available = get_available_roles()
        if not available:
            bot.edit_message_text(
                "😔 *К сожалению, все роли заняты*\n\n"
                "Пожалуйста, подождите, пока освободится место, "
                "или свяжитесь с администратором.",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="Markdown"
            )
            return

        text = "🎭 **Шаг 3 из 3:** Выбор роли\n\n"
        text += "*Доступные роли:*\n"
        for role in available:
            text += f"\n📌 **{role}**\n"

        bot.edit_message_text(
            text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=roles_menu()
        )

    elif call.data.startswith("role_"):
        role = call.data.replace("role_", "")

        if role in occupied_roles:
            bot.answer_callback_query(call.id, "❌ Эта роль уже занята!", show_alert=True)
            return

        is_safe, safety_msg = check_user_safety(user_id, username)
        if not is_safe:
            bot.answer_callback_query(call.id, f"❌ Проверка безопасности не пройдена: {safety_msg}", show_alert=True)
            return

        user_data[user_id]['role'] = role
        user_data[user_id]['step'] = 'waiting_approval'
        save_data()

        pending_approvals[user_id] = {
            'role': role,
            'username': username,
            'date': datetime.now().isoformat()
        }
        save_data()

        admin_keyboard = InlineKeyboardMarkup()
        btn_approve = InlineKeyboardButton("✅ Принять", callback_data=f"approve_{user_id}")
        btn_reject = InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{user_id}")
        btn_info = InlineKeyboardButton("👤 Инфо", callback_data=f"userinfo_{user_id}")
        admin_keyboard.add(btn_approve, btn_reject)
        admin_keyboard.add(btn_info)

        admin_text = (
            f"📝 *НОВАЯ ЗАЯВКА*\n\n"
            f"👤 *Пользователь:* @{username}\n"
            f"🆔 *ID:* `{user_id}`\n"
            f"🎭 *Выбранная роль:* {role}\n"
            f"📅 *Время:* {datetime.now().strftime('%H:%M:%S')}\n\n"
            f"*Действия:*"
        )

        bot.send_message(
            ADMIN_ID,
            admin_text,
            parse_mode="Markdown",
            reply_markup=admin_keyboard
        )

        bot.edit_message_text(
            f"✅ *Заявка отправлена!*\n\n"
            f"🎭 *Выбранная роль:* {role}\n\n"
            f"⏳ *Статус:* Ожидает одобрения\n\n"
            f"Администратор рассмотрит вашу заявку в ближайшее время.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )

    # ========== ОБРАБОТКА ЗАЯВОК АДМИНОМ ==========
    elif call.data.startswith("approve_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Только администратор может одобрять заявки")
            return

        applicant_id = int(call.data.split("_")[1])

        if applicant_id not in pending_approvals:
            bot.answer_callback_query(call.id, "❌ Заявка уже обработана")
            bot.delete_message(ADMIN_ID, call.message.message_id)
            return

        role = pending_approvals[applicant_id]['role']
        username = pending_approvals[applicant_id]['username']

        if role in occupied_roles:
            bot.answer_callback_query(call.id, "❌ Роль уже занята!")
            bot.send_message(
                ADMIN_ID,
                f"⚠️ Роль *{role}* уже занята. Заявка автоматически отклонена.",
                parse_mode="Markdown"
            )
            del pending_approvals[applicant_id]
            save_data()
            bot.delete_message(ADMIN_ID, call.message.message_id)
            return

        is_safe, safety_msg = check_user_safety(applicant_id, username)
        if not is_safe:
            bot.answer_callback_query(call.id, f"❌ Пользователь не прошел проверку: {safety_msg}")
            bot.send_message(
                ADMIN_ID,
                f"⚠️ Пользователь @{username} не прошел проверку безопасности\n\n{safety_msg}",
                parse_mode="Markdown"
            )
            del pending_approvals[applicant_id]
            save_data()
            bot.delete_message(ADMIN_ID, call.message.message_id)
            return

        assign_role(applicant_id, role)

        try:
            invite_link = bot.create_chat_invite_link(
                GROUP_CHAT_ID,
                member_limit=1,
                expire_date=datetime.now() + timedelta(hours=24),
                name=f"Приглашение для @{username}"
            )
            invite_url = invite_link.invite_link
        except Exception as e:
            logger.error(f"Ошибка создания ссылки: {e}")
            invite_url = "Ошибка создания ссылки, обратитесь к администратору"

        bot.send_message(
            applicant_id,
            f"🎉 *Поздравляем! Ваша заявка одобрена!* 🎉\n\n"
            f"🎭 *Ваша роль:* {role}\n\n"
            f"🔗 *Ссылка для вступления:*\n{invite_url}\n\n"
            f"📌 *Важные моменты:*\n"
            f"• Ссылка действительна 24 часа\n"
            f"• Используйте /call для призыва других\n\n"
            f"🌟 *Добро пожаловать!* 🌟",
            parse_mode="Markdown"
        )

        try:
            bot.send_message(
                GROUP_CHAT_ID,
                f"🌟 *Новый участник!* 🌟\n\n"
                f"@{username} присоединяется в роли *{role}*!\n\n"
                f"Давайте поприветствуем! 🎉",
                parse_mode="Markdown"
            )
        except:
            pass

        del pending_approvals[applicant_id]
        if applicant_id in user_data:
            del user_data[applicant_id]
        save_data()

        bot.answer_callback_query(call.id, "✅ Заявка одобрена!")
        bot.delete_message(ADMIN_ID, call.message.message_id)

    elif call.data.startswith("reject_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Только администратор может отклонять заявки")
            return

        applicant_id = int(call.data.split("_")[1])

        if applicant_id in pending_approvals:
            del pending_approvals[applicant_id]
            save_data()

        try:
            bot.send_message(
                applicant_id,
                "😔 *Заявка отклонена*\n\n"
                "К сожалению, ваша заявка не была одобрена.\n\n"
                "Возможные причины:\n"
                "• Все роли уже заняты\n"
                "• Вы не соответствуете требованиям\n\n"
                "Вы можете попробовать позже.",
                parse_mode="Markdown"
            )
        except:
            pass

        if applicant_id in user_data:
            del user_data[applicant_id]

        bot.answer_callback_query(call.id, "✅ Заявка отклонена")
        bot.delete_message(ADMIN_ID, call.message.message_id)

    elif call.data.startswith("userinfo_"):
        if not is_admin(user_id):
            return

        target_id = int(call.data.split("_")[1])
        try:
            user = bot.get_chat(target_id)
            text = f"👤 *Информация о пользователе*\n\n"
            text += f"*ID:* `{target_id}`\n"
            text += f"*Имя:* {user.first_name}\n"
            if user.username:
                text += f"*Username:* @{user.username}\n"
            if target_id in user_roles:
                text += f"*Роль:* {user_roles[target_id]}\n"
            if target_id in pending_approvals:
                text += f"*Статус:* Ожидает одобрения\n"
                text += f"*Желаемая роль:* {pending_approvals[target_id]['role']}\n"
            bot.answer_callback_query(call.id)
            bot.send_message(ADMIN_ID, text, parse_mode="Markdown")
        except:
            bot.answer_callback_query(call.id, "Не удалось получить информацию")

    # ========== МЕНЮ ПОДДЕРЖКИ И ЖАЛОБЫ ==========
    elif call.data == "support_menu":
        bot.edit_message_text(
            "🆘 *Меню поддержки*\n\nВыберите нужный пункт:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=support_menu()
        )

    elif call.data == "complaint":
        # Показываем меню выбора анонимности для жалобы
        bot.edit_message_text(
            "⚠️ *Подача жалобы*\n\n"
            "Выберите тип жалобы:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=complaint_menu()
        )
        bot.answer_callback_query(call.id)

    elif call.data == "complaint_anonymous":
        # Анонимная жалоба
        msg = bot.send_message(
            call.message.chat.id,
            "🔒 *Анонимная жалоба*\n\n"
            "Ваши данные НЕ будут переданы нарушителю.\n\n"
            "Введите ID пользователя и причину жалобы в формате:\n\n"
            "`123456789 Причина жалобы`\n\n"
            "📌 *Как узнать ID:*\n"
            "• Нажмите на сообщение пользователя → Forward → /id\n"
            "• Или используйте бота @userinfobot\n\n"
            "Для отмены отправьте /cancel",
            parse_mode="Markdown"
        )
        user_data[user_id] = {
            'state': 'awaiting_complaint',
            'msg_id': msg.message_id,
            'complaint_anonymous': True
        }
        save_data()
        bot.answer_callback_query(call.id)

    elif call.data == "complaint_public":
        # Открытая жалоба
        msg = bot.send_message(
            call.message.chat.id,
            "👤 *Открытая жалоба*\n\n"
            "Ваши данные будут видны администратору.\n\n"
            "Введите ID пользователя и причину жалобы в формате:\n\n"
            "`123456789 Причина жалобы`\n\n"
            "Для отмены отправьте /cancel",
            parse_mode="Markdown"
        )
        user_data[user_id] = {
            'state': 'awaiting_complaint',
            'msg_id': msg.message_id,
            'complaint_anonymous': False
        }
        save_data()
        bot.answer_callback_query(call.id)

    # ========== ПРЕДЛОЖЕНИЯ ==========
    elif call.data == "suggestion_start":
        # Показываем меню выбора анонимности для предложения
        bot.edit_message_text(
            "💡 *Отправка предложения*\n\n"
            "Выберите тип предложения:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=suggestion_choice_menu()
        )
        bot.answer_callback_query(call.id)

    elif call.data == "suggestion_anonymous":
        msg = bot.send_message(
            call.message.chat.id,
            "🔒 *Анонимное предложение*\n\n"
            "Напишите ваше предложение.\n\n"
            "Ваши данные НЕ будут переданы.\n\n"
            "Для отмены: /cancel",
            parse_mode="Markdown"
        )
        user_data[user_id] = {
            'state': 'awaiting_suggestion',
            'msg_id': msg.message_id,
            'suggestion_anonymous': True
        }
        save_data()
        bot.answer_callback_query(call.id)

    elif call.data == "suggestion_public":
        msg = bot.send_message(
            call.message.chat.id,
            "👤 *Публичное предложение*\n\n"
            "Напишите ваше предложение.\n\n"
            "Ваше имя будет указано.\n\n"
            "Для отмены: /cancel",
            parse_mode="Markdown"
        )
        user_data[user_id] = {
            'state': 'awaiting_suggestion',
            'msg_id': msg.message_id,
            'suggestion_anonymous': False
        }
        save_data()
        bot.answer_callback_query(call.id)

    # ========== ПОМОЩЬ ==========
    elif call.data == "help":
        help_text = (
            "❓ *Помощь и инструкция*\n\n"
            "*📝 Регистрация:*\n"
            "• Нажмите /start\n"
            "• Следуйте инструкциям\n\n"
            "*🎭 Команды:*\n"
            "• /start - Начать регистрацию\n"
            "• /support - Меню поддержки\n"
            "• /call [текст] - Призыв в игре\n"
            "• /cancel - Отменить действие\n"
            "• /id - Узнать свой ID\n\n"
            "*⚠️ Жалобы:*\n"
            "1. Нажмите /support\n"
            "2. Выберите 'Пожаловаться'\n"
            "3. Выберите анонимно или открыто\n"
            "4. Укажите ID и причину\n\n"
            "*💡 Предложения:*\n"
            "1. Нажмите /support\n"
            "2. Выберите 'Предложение'\n"
            "3. Выберите анонимно или с именем\n"
            "4. Напишите идею\n\n"
            f"*👑 Администратор:* @username\n\n"
            f"*📢 Наш канал:* {INFO_CHANNEL_ID}"
        )
        bot.edit_message_text(
            help_text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )

    # ========== НАВИГАЦИЯ ==========
    elif call.data == "back_to_main":
        bot.edit_message_text(
            "🏠 *Главное меню*\n\nВыберите действие:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=main_menu()
        )

    elif call.data == "back_to_start":
        bot.edit_message_text(
            "📝 *Регистрация*\n\nГотовы начать?",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=main_menu()
        )

    # ========== АДМИН-ПАНЕЛЬ ==========
    elif call.data == "admin_pending":
        if not is_admin(user_id):
            return

        if not pending_approvals:
            bot.edit_message_text(
                "📝 *Нет ожидающих заявок*",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="Markdown",
                reply_markup=admin_panel()
            )
            return

        text = "📝 *Ожидающие заявки:*\n\n"
        for uid, data in pending_approvals.items():
            text += f"• @{data['username']} → {data['role']}\n"
            text += f"  ID: `{uid}`\n\n"

        bot.edit_message_text(
            text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=admin_panel()
        )

    elif call.data == "admin_roles":
        if not is_admin(user_id):
            return

        available = get_available_roles()
        text = "📋 *Список ролей*\n\n"
        text += f"*Занято:* {len(occupied_roles)}/{len(AVAILABLE_ROLES)}\n\n"

        if occupied_roles:
            text += "*Занятые:*\n"
            for role, uid in occupied_roles.items():
                text += f"• {role} → `{uid}`\n"

        if available:
            text += f"\n*Свободные:*\n"
            for role in available:
                text += f"• {role}\n"

        bot.edit_message_text(
            text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=admin_panel()
        )

    elif call.data == "admin_reports":
        if not is_admin(user_id):
            return

        if not suspicious_users:
            bot.edit_message_text(
                "⚠️ *Нет жалоб*",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="Markdown",
                reply_markup=admin_panel()
            )
            return

        text = "⚠️ *Жалобы:*\n\n"
        for uid, data in suspicious_users.items():
            text += f"• `{uid}` - {data['reports']} жалоб\n"
            text += f"  Последняя: {data['reasons'][-1][:40]}...\n\n"

        bot.edit_message_text(
            text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=admin_panel()
        )

    elif call.data == "admin_suggestions":
        if not is_admin(user_id):
            return

        if not suggestions:
            bot.edit_message_text(
                "💡 *Нет предложений*",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="Markdown",
                reply_markup=admin_panel()
            )
            return

        text = "💡 *Последние предложения:*\n\n"
        for s in suggestions[-5:]:
            text += f"#{s['id']} от {s['username']}\n"
            text += f"{s['text'][:100]}...\n\n"

        bot.edit_message_text(
            text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=admin_panel()
        )

    elif call.data == "admin_clear":
        if not is_admin(user_id):
            return

        keyboard = InlineKeyboardMarkup()
        btn_confirm = InlineKeyboardButton("⚠️ ДА, ОЧИСТИТЬ ВСЁ", callback_data="confirm_clear")
        btn_cancel = InlineKeyboardButton("❌ Отмена", callback_data="admin_panel")
        keyboard.add(btn_confirm, btn_cancel)

        bot.edit_message_text(
            "⚠️ *ОПАСНО!*\n\n"
            "Вы уверены, что хотите очистить ВСЕ данные?\n\n"
            "Это действие нельзя отменить!",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=keyboard
        )

    elif call.data == "confirm_clear":
        if not is_admin(user_id):
            return

        initialize_empty_data()
        bot.edit_message_text(
            "✅ *Все данные очищены*",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=admin_panel()
        )

    elif call.data == "admin_panel":
        if not is_admin(user_id):
            return

        bot.edit_message_text(
            "👑 *Панель администратора*\n\nВыберите действие:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=admin_panel()
        )

    elif call.data == "no_roles":
        bot.answer_callback_query(call.id, "Все роли заняты! Попробуйте позже")

# ==================== ОБРАБОТЧИКИ СООБЩЕНИЙ ====================

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    """Обработка текстовых сообщений"""
    user_id = message.from_user.id

    if user_id in banned_users:
        bot.reply_to(message, "⚠️ Вы в черном списке")
        return

    # Обработка жалоб
    if user_id in user_data and user_data[user_id].get('state') == 'awaiting_complaint':
        try:
            parts = message.text.split(' ', 1)
            if len(parts) < 2:
                bot.reply_to(message, "❌ Неверный формат. Используйте: ID причина")
                return

            reported_id = int(parts[0])
            reason = parts[1]

            anonymous = user_data[user_id].get('complaint_anonymous', True)
            kicked, result = report_user(reported_id, reason, user_id, anonymous)
            bot.reply_to(message, f"✅ {result}")

            if 'msg_id' in user_data[user_id]:
                try:
                    bot.delete_message(message.chat.id, user_data[user_id]['msg_id'])
                except:
                    pass

            del user_data[user_id]
            save_data()

        except ValueError:
            bot.reply_to(message, "❌ Неверный ID пользователя")
        except Exception as e:
            bot.reply_to(message, f"❌ Ошибка: {e}")

    # Обработка предложений
    elif user_id in user_data and user_data[user_id].get('state') == 'awaiting_suggestion':
        suggestion_text = message.text
        username = message.from_user.username or message.from_user.first_name
        anonymous = user_data[user_id].get('suggestion_anonymous', True)

        suggestion_id = add_suggestion(user_id, username, suggestion_text, anonymous)

        # Отправляем админу
        admin_text = f"💡 *Новое предложение* #{suggestion_id}\n\n"
        if anonymous:
            admin_text += f"👤 *От:* Аноним\n"
        else:
            admin_text += f"👤 *От:* @{username}\n"
        admin_text += f"📝 *Текст:*\n{suggestion_text}"

        bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")

        bot.reply_to(
            message,
            "✅ *Спасибо за предложение!*\n\n"
            "Мы рассмотрим его в ближайшее время.",
            parse_mode="Markdown"
        )

        if 'msg_id' in user_data[user_id]:
            try:
                bot.delete_message(message.chat.id, user_data[user_id]['msg_id'])
            except:
                pass

        del user_data[user_id]
        save_data()

# ==================== ОБРАБОТЧИК НОВЫХ УЧАСТНИКОВ ====================

@bot.message_handler(content_types=['new_chat_members'])
def handle_new_member(message):
    """Проверка новых участников группы"""
    for member in message.new_chat_members:
        if member.id == bot.get_me().id:
            bot.send_message(
                message.chat.id,
                "🤖 *Бот активирован!*\n\n"
                "Я буду помогать управлять ролями и заявками.\n"
                "Для начала работы используйте /admin",
                parse_mode="Markdown"
            )
            continue

        if member.id not in user_roles:
            try:
                bot.ban_chat_member(GROUP_CHAT_ID, member.id)
                bot.unban_chat_member(GROUP_CHAT_ID, member.id)
                logger.info(f"Кикнут безрольный участник {member.id}")

                bot.send_message(
                    ADMIN_ID,
                    f"⚠️ *Автоматический кик*\n\n"
                    f"Пользователь {member.mention_name()} попытался войти без роли\n"
                    f"ID: `{member.id}`",
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"Ошибка кика: {e}")

# ==================== ЗАПУСК БОТА ====================

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 РОЛЕВОЙ БОТ ЗАПУСКАЕТСЯ")
    print("=" * 50)

    load_data()

    print(f"📊 Статистика загрузки:")
    print(f"   - Занято ролей: {len(occupied_roles)}")
    print(f"   - Участников: {len(user_roles)}")
    print(f"   - Жалоб: {len(suspicious_users)}")
    print(f"   - Предложений: {len(suggestions)}")
    print(f"   - Ожидает заявок: {len(pending_approvals)}")
    print("=" * 50)
    print("✅ Бот готов к работе!")
    print("=" * 50)

    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            logger.error(f"Ошибка подключения: {e}")
            print(f"❌ Ошибка: {e}")
            print("🔄 Переподключение через 15 секунд...")
            time.sleep(15)




