import telebot
from telebot import TeleBot, types
import sqlite3


API_KEY = '6656804610:AAGg'
ADMIN_IDS = [5034091401, 6942137366]
CHANNEL_USERNAME = '@saidyshop'
DATABASE_NAME = 'your_database.db'


bot = TeleBot(API_KEY)


def create_users_table():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT
        )
    ''')
    conn.commit()
    conn.close()


create_users_table()


@bot.message_handler(commands=['admin'])
def admin_panel(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        markup = types.InlineKeyboardMarkup()
        send_broadcast_button = types.InlineKeyboardButton(text="СДЕЛАТЬ РАССЫЛКУ", callback_data='send_broadcast')
        show_users_button = types.InlineKeyboardButton(text="ПОКАЗАТЬ ЮЗЕРОВ", callback_data='show_users')
        markup.row(send_broadcast_button)
        markup.row(show_users_button)

        with open('photo.jpg', 'rb') as photo_file:
            bot.send_photo(message.chat.id, photo_file,caption='Панель администратора', reply_markup=markup)
        
    else:
        bot.send_message(message.chat.id, "У вас нет доступа к этой функции.")


def get_total_users():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_users_list():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, first_name, last_name FROM users")
    users = cursor.fetchall()
    conn.close()
    return users


def process_broadcast_message(message):
    # Проверяем, является ли отправитель сообщения админом
    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "У вас нет прав для выполнения этой операции.")
        return

    users = get_users_list()

    if message.photo:
        photo_file_id = message.photo[-1].file_id
        for user in users:
            bot.send_photo(user[0], photo_file_id, caption=message.caption)
    else:
        for user in users:
            bot.send_message(user[0], message.text)

    # Отправляем уведомление админу
    admin_notification = f"Рассылка отправлена {len(users)} пользователям."
    for admin_id in ADMIN_IDS:
        bot.send_message(admin_id, admin_notification)



@bot.message_handler(commands=['start'])
def main(message: types.Message):
    save_user(message.from_user)

    user_id = message.from_user.id
    res = bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)

    if res.status == "member" or res.status == 'creator':
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text="Апельсины", callback_data='apilsini')
        button1 = types.InlineKeyboardButton(text="Мандарины", callback_data='orang')
        button2 = types.InlineKeyboardButton(text="Яблоки", callback_data='appls')
        markup.row(button)
        markup.row(button1)
        markup.row(button2)

        # Открываем файл с фотографией
        with open('photo.jpg', 'rb') as photo_file:
            bot.send_photo(message.chat.id, photo_file, caption="Спасибо за подписку! Вы можете продолжить использование бота.", reply_markup=markup)

    else:
        markup = types.InlineKeyboardMarkup()

        check_subscription_button = types.InlineKeyboardButton(text="ПРОВЕРИТЬ ПОДПИСКУ", callback_data='check_subscription')
        open_channel = types.InlineKeyboardButton(text="Открыть канал", url='https://t.me/saidyshop')
        markup.add(check_subscription_button)
        markup.add(open_channel)

        bot.send_message(user_id, f'Добро пожаловать, {message.from_user.first_name}\n\nПеред началом подпишись на канал',
                         reply_markup=markup,
                         parse_mode="MarkdownV2")


def save_user(user):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Проверяем, существует ли пользователь с таким ID
    cursor.execute("SELECT id FROM users WHERE id=?", (user.id,))
    existing_user = cursor.fetchone()

    if existing_user:
        print("Пользователь уже существует в базе данных.")
    else:
        # Добавляем пользователя в базу данных
        cursor.execute("INSERT INTO users (id, username, first_name, last_name) VALUES (?, ?, ?, ?)",
                       (user.id, user.username, user.first_name, user.last_name))
        conn.commit()
        print("Пользователь успешно добавлен в базу данных.")

    conn.close()


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    message = call.message
    chat_id = message.chat.id

    if call.data == 'send_broadcast':
        bot.send_message(chat_id, "Отправьте сообщение для рассылки:")
        bot.register_next_step_handler(message, process_broadcast_message)

    elif call.data == 'show_users':
        total_users = get_total_users()
        bot.send_message(chat_id, f"В базе данных {total_users} пользователей.")

    elif call.data == 'apilsini':
        keyboard = types.InlineKeyboardMarkup()
        orange = types.InlineKeyboardButton(text="Абхазия", callback_data="abh")
        sth1 = types.InlineKeyboardButton(text="Ееще чтот", callback_data="sth1")
        sth2 = types.InlineKeyboardButton(text="Зеленые", callback_data="sth2")
        back = types.InlineKeyboardButton(text="Назад", callback_data="backk")
        keyboard.add(orange)
        keyboard.add(sth1)
        keyboard.add(sth2)
        keyboard.add(back)
        bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        with open('photo.jpg', 'rb') as photo_file:
            bot.send_photo(message.chat.id, photo_file, caption='Это раздел с апельсинами, выбери сорт',reply_markup=keyboard)

    elif call.data == 'orang':
        keyboard = types.InlineKeyboardMarkup()
        orange = types.InlineKeyboardButton(text="Мандариныыы", callback_data="apple")
        back = types.InlineKeyboardButton(text="Назад", callback_data="backk")
        keyboard.add(orange)
        keyboard.add(back)
        bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        with open('photo.jpg', 'rb') as photo_file:
            bot.send_photo(message.chat.id, photo_file, caption='Это раздел с мандаринами, выбери сорт',reply_markup=keyboard)

    elif call.data == 'appls':
        keyboard = types.InlineKeyboardMarkup()
        green = types.InlineKeyboardButton(text="Зеленые", callback_data="green")
        red = types.InlineKeyboardButton(text="Красные", callback_data="red")
        back = types.InlineKeyboardButton(text="Назад", callback_data="backk")
        keyboard.add(green)
        keyboard.add(red)
        keyboard.add(back)
        bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        with open('photo.jpg', 'rb') as photo_file:
            bot.send_photo(message.chat.id, photo_file, caption='Это раздел с яблоками, выбери сорт',reply_markup=keyboard)

    elif call.data == 'abh':
        keyboard = types.InlineKeyboardMarkup()
        back = types.InlineKeyboardButton(text="Назад🔙", callback_data="back1")
        keyboard.add(back)
        bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        with open('photo.jpg', 'rb') as photo_file:
            bot.send_photo(message.chat.id, photo_file, caption='Описание апельсинов', reply_markup=keyboard)

    elif call.data == 'sth1':
        keyboard = types.InlineKeyboardMarkup()
        back = types.InlineKeyboardButton(text="Назад🔙", callback_data="back1")
        keyboard.add(back)
        bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        with open('photo.jpg', 'rb') as photo_file:
            bot.send_photo(message.chat.id, photo_file, caption='Описание апельсинов', reply_markup=keyboard)

    elif call.data == 'sth2':
        keyboard = types.InlineKeyboardMarkup()
        back = types.InlineKeyboardButton(text="Назад🔙", callback_data="back1")
        keyboard.add(back)
        bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        with open('photo.jpg', 'rb') as photo_file:
            bot.send_photo(message.chat.id, photo_file, caption='Описание апельсинов', reply_markup=keyboard)

    elif call.data == 'apple':
        keyboard = types.InlineKeyboardMarkup()
        back = types.InlineKeyboardButton(text="Назад🔙", callback_data="back2")
        keyboard.add(back)
        bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        with open('photo.jpg', 'rb') as photo_file:
            bot.send_photo(message.chat.id, photo_file, caption='Описание мандаринов', reply_markup=keyboard)

    elif call.data == 'green':
        keyboard = types.InlineKeyboardMarkup()
        back = types.InlineKeyboardButton(text="Назад🔙", callback_data="back3")
        keyboard.add(back)
        bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        with open('photo.jpg', 'rb') as photo_file:
            bot.send_photo(message.chat.id, photo_file, caption='Описание яблочек', reply_markup=keyboard)

    elif call.data == 'red':
        keyboard = types.InlineKeyboardMarkup()
        back = types.InlineKeyboardButton(text="Назад🔙", callback_data="back3")
        keyboard.add(back)
        bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        with open('photo.jpg', 'rb') as photo_file:
            bot.send_photo(message.chat.id, photo_file, caption='Описание яблочек', reply_markup=keyboard)

    elif call.data == 'back1':
        keyboard = types.InlineKeyboardMarkup()
        orange = types.InlineKeyboardButton(text="Абхазия", callback_data="abh")
        sth1 = types.InlineKeyboardButton(text="Ееще чтот", callback_data="sth1")
        sth2 = types.InlineKeyboardButton(text="Зеленые", callback_data="sth2")
        back = types.InlineKeyboardButton(text="Назад", callback_data="backk")
        keyboard.add(orange)
        keyboard.add(sth1)
        keyboard.add(sth2)
        keyboard.add(back)
        bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        with open('photo.jpg', 'rb') as photo_file:
            bot.send_photo(message.chat.id, photo_file, caption='Это раздел с апельсинами, выбери сорт',reply_markup=keyboard)

    elif call.data == 'back2':
        keyboard = types.InlineKeyboardMarkup()
        orange = types.InlineKeyboardButton(text="Мандариныыы", callback_data="apple")
        back = types.InlineKeyboardButton(text="Назад", callback_data="backk")
        keyboard.add(orange)
        keyboard.add(back)
        bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        with open('photo.jpg', 'rb') as photo_file:
            bot.send_photo(message.chat.id, photo_file, caption='Это раздел с мандаринами, выбери сорт',reply_markup=keyboard)

    elif call.data == 'back3':
        keyboard = types.InlineKeyboardMarkup()
        green = types.InlineKeyboardButton(text="Зеленые", callback_data="green")
        red = types.InlineKeyboardButton(text="Красные", callback_data="red")
        back = types.InlineKeyboardButton(text="Назад", callback_data="backk")
        keyboard.add(green)
        keyboard.add(red)
        keyboard.add(back)
        bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        with open('photo.jpg', 'rb') as photo_file:
            bot.send_photo(message.chat.id, photo_file, caption='Это раздел с яблоками, выбери сорт',reply_markup=keyboard)
        

    elif call.data == 'backk':
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text="Апельсины", callback_data='apilsini')
        button3 = types.InlineKeyboardButton(text="Мандарины", callback_data='orang')
        button1 = types.InlineKeyboardButton(text="Яблоки", callback_data='appls')
        markup.add(button3)
        markup.add(button)
        markup.add(button1)
        bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        with open('photo.jpg', 'rb') as photo_file:
            bot.send_photo(message.chat.id, photo_file, caption="Вы в главном меню", reply_markup=markup)

    elif call.data == 'check_subscription':
        user_id = call.from_user.id
        res = bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if res.status == "member" or res.status == 'creator':
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton(text="Апельсины", callback_data='apilsini')
            button3 = types.InlineKeyboardButton(text="Мандарины", callback_data='orang')
            button1 = types.InlineKeyboardButton(text="Яблоки", callback_data='appls')
            markup.row(button3, button, button1)

            with open('photo.jpg', 'rb') as photo_file:
                bot.send_photo(call.message.chat.id, photo_file, caption="Спасибо за подписку! Вы можете продолжить использование бота.", reply_markup=markup)

            bot.send_message(user_id, "Вы подписаны на канал.")
        else:
            bot.send_message(call.message.chat.id, f"Пожалуйста, подпишитесь на канал {CHANNEL_USERNAME} для доступа к функциям бота.")



bot.polling(none_stop=True)
