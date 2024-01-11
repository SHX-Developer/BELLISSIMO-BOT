from telebot import telebot, types
import sqlite3
import datetime
import time

import config

import inline_markups
import reply_markups


#  LIBRARY VARIABLES  #

bot = telebot.TeleBot(config.token)

db = sqlite3.connect("bellissimo_database.db", check_same_thread=False)
sql = db.cursor()

date_time = datetime.datetime.now().date()

cities = ["Ташкент", "Самарканд", "Андижан", "Коканд", "Фергана", "Чирчик", "Наманган", "Бухара", "Алмалык", "Нурафшон"]




#  CREATING DATABASES

sql.execute('CREATE TABLE IF NOT EXISTS user_access (id INTEGER, username TEXT, firstname TEXT, lastname TEXT, date TIMESTAMP)')
sql.execute('CREATE TABLE IF NOT EXISTS user_action (id INTEGER, pizza TEXT, size TEXT, dough TEXT, count INTEGER, price INTEGER, description TEXT)')
sql.execute('CREATE TABLE IF NOT EXISTS user_address (id INTEGER, delivery TEXT, address TEXT, home TEXT, flat TEXT, code TEXT, floor TEXT, entrance TEXT)')
sql.execute('CREATE TABLE IF NOT EXISTS user_data (id INTEGER, firstname TEXT, lastname TEXT, contact TEXT, city TEXT)')
db.commit()





#  START COMMAND

@bot.message_handler(commands = ["start"])
def start(message):

    sql.execute("SELECT id FROM user_access WHERE id = ?", (message.chat.id,))
    user_id = sql.fetchone()

    if user_id is None:

        sql.execute(f'CREATE TABLE IF NOT EXISTS cart_{message.chat.id} (number INTEGER PRIMARY KEY, pizza TEXT, size TEXT, dough TEXT, count INTEGER, price INTEGER, description TEXT)')

        sql.execute('INSERT INTO user_access (id, username, firstname, lastname, date) VALUES (?, ?, ?, ?, ?)',
        (message.chat.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name, date_time))

        sql.execute(f'INSERT INTO user_data (id, firstname, lastname, contact, city) VALUES (?, ?, ?, ?, ?)',
        (message.chat.id, "-", "-", "-", "-"))

        sql.execute(f'INSERT INTO user_address (id, delivery, address, home, flat, code, floor, entrance) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (message.chat.id, "-", "-", "-", "-", "-", "-", "-"))

        sql.execute(f'INSERT INTO user_action (id, pizza, size, dough, count, price, description) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (message.chat.id, "-", "-", "-", "-", "-", "-"))

        db.commit()

        bot.send_message(message.chat.id, f"Выберите язык:", reply_markup = reply_markups.language_button)

    else:

        bot.send_message(message.chat.id, f"Выберите язык:", reply_markup = reply_markups.language_button)





#  GET CONTACT

@bot.message_handler(content_types = ["contact"])
def get_contact(message):

    sql.execute('SELECT contact FROM user_data WHERE id = ?', (message.chat.id,))
    user_contact = sql.fetchone()[0]

    if user_contact == "-":

        sql.execute('UPDATE user_data SET contact = ? WHERE id = ?', (message.contact.phone_number, message.chat.id))
        db.commit()

        user_city = bot.send_message(message.chat.id, "Пожалуйста, выберите город, в котором вы живёте 👇", reply_markup = reply_markups.city_button)
        bot.register_next_step_handler(user_city, check_city)

    else:

        bot.send_message(message.chat.id,"Выберите раздел:", reply_markup = reply_markups.menu_button)

#  CHECK CITY

def check_city(message):

    if any(city in message.text for city in cities):

        sql.execute('UPDATE user_data SET city = ? WHERE id = ?', (message.text, message.chat.id))
        db.commit()

        bot.send_message(message.chat.id,"Выберите раздел:", reply_markup = reply_markups.menu_button)

    else:

        bot.send_message(message.chat.id,"❌ Что-то пошло не так, попробуйте снова")
        get_city(message)

#  GET CITY

def get_city(message):

    user_city = bot.send_message(message.chat.id, "Пожалуйста, выберите город, в котором вы живёте 👇", reply_markup = reply_markups.city_button)
    bot.register_next_step_handler(user_city, check_city)





#  TEXT

@bot.message_handler(content_types = ["text"])
def text(message):

    sql.execute('SELECT id FROM user_access WHERE id = ?', (message.chat.id,))
    user_id = sql.fetchone()[0]





#  LANGUAGE

    if message.text == "🇷🇺 Русский":
        bot.send_message(user_id, "Отправьте или введите свой номер телефона 👇  в виде:\n<b>+998 ** *** ****</b>", parse_mode = "html", reply_markup = reply_markups.contact_button)

    elif message.text == "🇺🇿 O'zbekcha":
        bot.send_message(user_id, "Отправьте или введите свой номер телефона 👇  в виде:\n<b>+998 ** *** ****</b>", parse_mode = "html", reply_markup = reply_markups.contact_button)






#  MENU

    elif message.text == "🛍 Заказать":
        bot.send_message(user_id, f"Рады вас видеть, {message.from_user.first_name} ! Что будете заказывать сегодня 🍕", parse_mode = "html", reply_markup = reply_markups.category_button)











#  CATEGORY

    elif message.text == "🍕 Пицца":
        bot.send_message(user_id, "Выберите пиццу 🍕", parse_mode = "html", reply_markup = reply_markups.pizza_button)










#  CART

    elif message.text == "📥 Корзина":

        sql.execute(f'SELECT pizza FROM cart_{user_id}')
        user_cart = sql.fetchone()

        if user_cart == None:

            bot.send_message(user_id, "Ваша корзина ещё пуста 😕 Давайте наполним её 📥")
            bot.send_message(message.chat.id, f"Рады вас видеть, {message.from_user.first_name} ! Что будете заказывать сегодня 🍕", reply_markup = reply_markups.category_button)

        else:

            bot.send_message(user_id, "<b>📥 Корзина</b>", parse_mode = "html", reply_markup = reply_markups.cart_button)
            bot.send_message(user_id,   f"<b>Тип заказа:</b> 🚙 Доставка"
                                        f"\n<b>📍 Адрес</b>"
                                        f"\n🏠 Дом №: <b>-</b>"
                                        f"\n🛎 Кв./офис: <b>-</b>"
                                        f"\n🔒 Код двери: <b>-</b>"
                                        f"\n🪜 Этаж: <b>-</b>"
                                        f"\n🚪 Подъезд: <b>-</b>",
                                        parse_mode="html", reply_markup = inline_markups.edit_address)

            sql.execute(f'SELECT * FROM cart_{user_id}')
            data = sql.fetchall()

            total_sum = 0
            message_text = ""

            for row in data:
                pizza = row[1]
                size = row[2]
                count = row[4]
                price = row[5]

                total = price * count
                total_sum += total
                result = "{: ,}".format(total_sum).replace(",", " ")
                message_text += f"<b>{count} x</b> {pizza} {size}\n"

            bot.send_message(user_id, message_text, parse_mode="html", reply_markup = inline_markups.edit_cart)
            bot.send_message(user_id, f"<b>Итого:</b>{result} сум", parse_mode="html", reply_markup = None)





#  ADD TO CART

    elif message.text == "Хочу 😍":

        sql.execute('SELECT * FROM user_action WHERE id = ?', (message.chat.id,))
        data = sql.fetchone()
        pizza = data[1]; size = data[2]; dough = data[3]; count = data[4]; price = data[5]; description = data[6]

        sql.execute(f'INSERT INTO cart_{user_id} (pizza, size, dough, count, price, description) VALUES (?, ?, ?, ?, ?, ?)',
        (pizza, size, dough, count, price, description))
        db.commit()

        bot.send_message(user_id, f"Товар {pizza} успешно добавлен в корзину 📥 Закажем что-нибудь еще?", reply_markup=reply_markups.pizza_button)
        bot.send_message(user_id, "Выберите пиццу 🍕", parse_mode = "html", reply_markup = reply_markups.pizza_button)

        bot.delete_message(message.chat.id, message.message_id)
        bot.delete_message(message.chat.id, message.message_id - 1)
        bot.delete_message(message.chat.id, message.message_id - 2)










#  BACK BUTTONS

    elif message.text == "⬅️ Назад":
        bot.send_message(user_id, f"Рады вас видеть, {message.from_user.first_name} ! Что будете заказывать сегодня 🍕", parse_mode = "html", reply_markup = reply_markups.category_button)

    elif message.text == "⬅️  Назад":
        bot.send_message(user_id, "Выберите пиццу 🍕", parse_mode = "html", reply_markup = reply_markups.pizza_button)
        bot.delete_message(message.chat.id, message.message_id)
        bot.delete_message(message.chat.id, message.message_id - 1)
        bot.delete_message(message.chat.id, message.message_id - 2)









#  CLEAR CART

    elif message.text == "🔄 Очистить":
        sql.execute(f'SELECT pizza FROM cart_{user_id}')
        user_cart = sql.fetchone()

        if user_cart == None:

            bot.send_message(user_id, "Ваша корзина ещё пуста 😕 Давайте наполним её 📥")
            bot.send_message(message.chat.id, f"Рады вас видеть, {message.from_user.first_name} ! Что будете заказывать сегодня 🍕", reply_markup = reply_markups.category_button)

        else:

            sql.execute(f'DELETE FROM cart_{user_id}')
            db.commit()

            bot.send_message(user_id, "Ваша корзина ещё пуста 😕 Давайте наполним её 📥")
            bot.send_message(message.chat.id, f"Рады вас видеть, {message.from_user.first_name} ! Что будете заказывать сегодня 🍕", reply_markup = reply_markups.category_button)

            try:

                bot.delete_message(message.chat.id, message.message_id)
                bot.delete_message(message.chat.id, message.message_id - 1)
                bot.delete_message(message.chat.id, message.message_id - 2)
                bot.delete_message(message.chat.id, message.message_id - 3)
                bot.delete_message(message.chat.id, message.message_id - 4)

            except:

                pass








    #  PIZZA

    else:

        sql.execute('SELECT * FROM pizza WHERE pizza = ?', (message.text,))
        data = sql.fetchone()
        number = data[0]; pizza = data[1]; small = data[2]; medium = data[3]; big = data[4]; description = data[5]

        if data:

            if small == "-":

                sql.execute('UPDATE user_action SET pizza = ? WHERE id = ?', (pizza, user_id))
                sql.execute('UPDATE user_action SET size = ? WHERE id = ?', ("большая", user_id))
                sql.execute('UPDATE user_action SET dough = ? WHERE id = ?', ("Тонкое", user_id))
                sql.execute('UPDATE user_action SET count = ? WHERE id = ?', (1, user_id))
                sql.execute('UPDATE user_action SET price = ? WHERE id = ?', (big, user_id))
                sql.execute('UPDATE user_action SET description = ? WHERE id = ?', (description, user_id))
                db.commit()

                sql.execute('SELECT * FROM user_action WHERE id = ?', (user_id,))
                data = sql.fetchone()
                pizza = data[1]; size = data[2]; dough = data[3]; count = data[4]; price = data[5]; description = data[6]

                result = price * count
                total = "{: ,}".format(result).replace(",", " ")

                inline = types.InlineKeyboardMarkup()
                inline.row(types.InlineKeyboardButton(text = f"{'✅ Большая' if size == 'большая' else 'Большая'}", callback_data = f"-"))
                inline.row(types.InlineKeyboardButton(text = f"{'✅ Тонкое' if dough == 'Тонкое' else 'Тонкое'}", callback_data = f"bigthin_{number}"),
                           types.InlineKeyboardButton(text = f"{'✅ Воздушное' if dough == 'Воздушное' else 'Воздушное'}", callback_data = f"bigair_{number}"),
                           types.InlineKeyboardButton(text = f"{'✅ Хот-дог борт' if dough == 'Хот-дог борт' else 'Хот-дог борт'}", callback_data = f"hotdog_{number}"))
                inline.row(types.InlineKeyboardButton(text = "➖", callback_data = f"bigminus_{number}"),
                           types.InlineKeyboardButton(text = f"{count}", callback_data = f"add"),
                           types.InlineKeyboardButton(text = "➕", callback_data = f"bigplus_{number}"))
                inline.row(types.InlineKeyboardButton(text = f"Хочу 😍", callback_data = f"add"))

            else:

                sql.execute('UPDATE user_action SET pizza = ? WHERE id = ?', (pizza, user_id))
                sql.execute('UPDATE user_action SET size = ? WHERE id = ?', ("маленькая", user_id))
                sql.execute('UPDATE user_action SET dough = ? WHERE id = ?', ("Воздушное", user_id))
                sql.execute('UPDATE user_action SET count = ? WHERE id = ?', (1, user_id))
                sql.execute('UPDATE user_action SET price = ? WHERE id = ?', (small, user_id))
                sql.execute('UPDATE user_action SET description = ? WHERE id = ?', (description, user_id))
                db.commit()

                sql.execute('SELECT * FROM user_action WHERE id = ?', (user_id,))
                data = sql.fetchone()
                pizza = data[1]; size = data[2]; dough = data[3]; count = data[4]; price = data[5]; description = data[6]
                result = price * count
                total = "{: ,}".format(result).replace(",", " ")

                inline = types.InlineKeyboardMarkup()
                inline.row(types.InlineKeyboardButton(text = f"{'✅ Маленькая' if size == 'маленькая' else 'Маленькая'}", callback_data = f"small_{number}"),
                           types.InlineKeyboardButton(text = f"{'✅ Средняя' if size == 'средняя' else 'Средняя'}", callback_data = f"medium_{number}"),
                           types.InlineKeyboardButton(text = f"{'✅ Большая' if size == 'большая' else 'Большая'}", callback_data = f"big_{number}"))
                inline.row(types.InlineKeyboardButton(text = f"{'✅ Воздушное' if dough == 'Воздушное' else 'Воздушное'}", callback_data = f"smallair_{number}"))
                inline.row(types.InlineKeyboardButton(text = "➖", callback_data = f"smallminus_{number}"),
                           types.InlineKeyboardButton(text = f"{count}", callback_data = f"add"),
                           types.InlineKeyboardButton(text = "➕", callback_data = f"smallplus_{number}"))
                inline.row(types.InlineKeyboardButton(text = f"Хочу 😍", callback_data = f"add"))

            text = (
            f"{pizza} {size}"
            f"\n\nТесто: <b>{dough}</b>"
            f"\n\n{description}"
            f"\n\nЦена:<b>{total} сум</b>")

            bot.send_message(user_id, "Выберите размер пиццы и модификатор:", reply_markup=reply_markups.action_button)
            with open(f"photo/{number}.jpg", "rb") as photo:
                bot.send_photo(user_id, photo, caption = text, parse_mode = "html", reply_markup = inline)
                bot.delete_message(message.chat.id, message.message_id)
                bot.delete_message(message.chat.id, message.message_id - 1)








#  CALLBACK  #

@bot.callback_query_handler(func = lambda call: True)
def callback(call):

    sql.execute('SELECT id FROM user_access WHERE id = ?', (call.message.chat.id,))
    user_id = sql.fetchone()[0]



#  SMALL

    if call.data.startswith("small_"):
        number = call.data.split("_")[1]

        sql.execute('SELECT * FROM pizza WHERE number = ?', (number,))
        data = sql.fetchone()
        number = data[0]; pizza = data[1]; small = data[2]; medium = data[3]; big = data[4]; description = data[5]

        sql.execute('UPDATE user_action SET size = ? WHERE id = ?', ("маленькая", user_id))
        sql.execute('UPDATE user_action SET dough = ? WHERE id = ?', ("Воздушное", user_id))
        sql.execute('UPDATE user_action SET price = ? WHERE id = ?', (small, user_id))
        db.commit()

        sql.execute('SELECT * FROM user_action WHERE id = ?', (call.message.chat.id,))
        data = sql.fetchone()
        pizza = data[1]; size = data[2]; dough = data[3]; count = data[4]; price = data[5]; description = data[6]
        result = price * count
        total = "{: ,}".format(result).replace(",", " ")

        inline = types.InlineKeyboardMarkup()
        inline.row(types.InlineKeyboardButton(text = f"{'✅ Маленькая' if size == 'маленькая' else 'Маленькая'}", callback_data = f"small_{number}"),
                   types.InlineKeyboardButton(text = f"{'✅ Средняя' if size == 'средняя' else 'Средняя'}", callback_data = f"medium_{number}"),
                   types.InlineKeyboardButton(text = f"{'✅ Большая' if size == 'большая' else 'Большая'}", callback_data = f"big_{number}"))
        inline.row(types.InlineKeyboardButton(text = f"{'✅ Воздушное' if dough == 'Воздушное' else 'Воздушное'}", callback_data = f"smallair_{number}"))
        inline.row(types.InlineKeyboardButton(text = "➖", callback_data = f"smallminus_{number}"),
                   types.InlineKeyboardButton(text = f"{count}", callback_data = f"add"),
                   types.InlineKeyboardButton(text = "➕", callback_data = f"smallplus_{number}"))
        inline.row(types.InlineKeyboardButton(text = f"Хочу 😍", callback_data = f"add"))

        text = (
        f"{pizza} {size}"
        f"\n\nТесто: <b>{dough}</b>"
        f"\n\n{description}"
        f"\n\nЦена:<b>{total} сум</b>")

        with open(f"photo/{number}.jpg", "rb") as photo:
            bot.edit_message_media(
            media = telebot.types.InputMedia(
            type = 'photo',
            media = photo,
            caption = text,
            parse_mode ="html"),
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            reply_markup = inline)





#  MEDIUM

    elif call.data.startswith("medium_"):
        number = call.data.split("_")[1]

        sql.execute('SELECT * FROM pizza WHERE number = ?', (number,))
        data = sql.fetchone()
        number = data[0]; pizza = data[1]; small = data[2]; medium = data[3]; big = data[4]; description = data[5]

        sql.execute('UPDATE user_action SET size = ? WHERE id = ?', ("средняя", user_id))
        sql.execute('UPDATE user_action SET dough = ? WHERE id = ?', ("Тонкое", user_id))
        sql.execute('UPDATE user_action SET price = ? WHERE id = ?', (medium, user_id))
        db.commit()

        sql.execute('SELECT * FROM user_action WHERE id = ?', (call.message.chat.id,))
        data = sql.fetchone()
        pizza = data[1]; size = data[2]; dough = data[3]; count = data[4]; price = data[5]; description = data[6]
        result = price * count
        total = "{: ,}".format(result).replace(",", " ")

        inline = types.InlineKeyboardMarkup()
        inline.row(types.InlineKeyboardButton(text = f"{'✅ Маленькая' if size == 'маленькая' else 'Маленькая'}", callback_data = f"small_{number}"),
                   types.InlineKeyboardButton(text = f"{'✅ Средняя' if size == 'средняя' else 'Средняя'}", callback_data = f"medium_{number}"),
                   types.InlineKeyboardButton(text = f"{'✅ Большая' if size == 'большая' else 'Большая'}", callback_data = f"big_{number}"))
        inline.row(types.InlineKeyboardButton(text = f"{'✅ Тонкое' if dough == 'Тонкое' else 'Тонкое'}", callback_data = f"mediumthin_{number}"),
                   types.InlineKeyboardButton(text = f"{'✅ Воздушное' if dough == 'Воздушное' else 'Воздушное'}", callback_data = f"mediumair_{number}"))
        inline.row(types.InlineKeyboardButton(text = "➖", callback_data = f"mediumminus_{number}"),
                   types.InlineKeyboardButton(text = f"{count}", callback_data = f"add"),
                   types.InlineKeyboardButton(text = "➕", callback_data = f"mediumplus_{number}"))
        inline.row(types.InlineKeyboardButton(text = f"Хочу 😍", callback_data = f"add"))

        text = (
        f"{pizza} {size}"
        f"\n\nТесто: <b>{dough}</b>"
        f"\n\n{description}"
        f"\n\nЦена:<b>{total} сум</b>")

        with open(f"photo/{number}.jpg", "rb") as photo:
            bot.edit_message_media(
            media = telebot.types.InputMedia(
            type = 'photo',
            media = photo,
            caption = text,
            parse_mode ="html"),
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            reply_markup = inline)





#  BIG

    elif call.data.startswith("big_"):
        number = call.data.split("_")[1]

        sql.execute('SELECT * FROM pizza WHERE number = ?', (number,))
        data = sql.fetchone()
        number = data[0]; pizza = data[1]; small = data[2]; medium = data[3]; big = data[4]; description = data[5]

        sql.execute('UPDATE user_action SET size = ? WHERE id = ?', ("большая", user_id))
        sql.execute('UPDATE user_action SET dough = ? WHERE id = ?', ("Тонкое", user_id))
        sql.execute('UPDATE user_action SET price = ? WHERE id = ?', (big, user_id))
        db.commit()

        sql.execute('SELECT * FROM user_action WHERE id = ?', (call.message.chat.id,))
        data = sql.fetchone()
        pizza = data[1]; size = data[2]; dough = data[3]; count = data[4]; price = data[5]; description = data[6]
        result = price * count
        total = "{: ,}".format(result).replace(",", " ")

        inline = types.InlineKeyboardMarkup()
        inline.row(types.InlineKeyboardButton(text = f"{'✅ Маленькая' if size == 'маленькая' else 'Маленькая'}", callback_data = f"small_{number}"),
                   types.InlineKeyboardButton(text = f"{'✅ Средняя' if size == 'средняя' else 'Средняя'}", callback_data = f"medium_{number}"),
                   types.InlineKeyboardButton(text = f"{'✅ Большая' if size == 'большая' else 'Большая'}", callback_data = f"big_{number}"))
        inline.row(types.InlineKeyboardButton(text = f"{'✅ Тонкое' if dough == 'Тонкое' else 'Тонкое'}", callback_data = f"bigthin_{number}"),
                   types.InlineKeyboardButton(text = f"{'✅ Воздушное' if dough == 'Воздушное' else 'Воздушное'}", callback_data = f"bigair_{number}"),
                   types.InlineKeyboardButton(text = f"{'✅ Хот-дог борт' if dough == 'Хот-дог борт' else 'Хот-дог борт'}", callback_data = f"hotdog_{number}"))
        inline.row(types.InlineKeyboardButton(text = "➖", callback_data = f"bigminus_{number}"),
                   types.InlineKeyboardButton(text = f"{count}", callback_data = f"add"),
                   types.InlineKeyboardButton(text = "➕", callback_data = f"bigplus_{number}"))
        inline.row(types.InlineKeyboardButton(text = f"Хочу 😍", callback_data = f"add"))

        text = (
        f"{pizza} {size}"
        f"\n\nТесто: <b>{dough}</b>"
        f"\n\n{description}"
        f"\n\nЦена:<b>{total} сум</b>")

        with open(f"photo/{number}.jpg", "rb") as photo:
            bot.edit_message_media(
            media = telebot.types.InputMedia(
            type = 'photo',
            media = photo,
            caption = text,
            parse_mode ="html"),
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            reply_markup = inline)





#  DOUGH

    #  MEDIUM

    elif call.data.startswith("mediumthin_"):
        number = call.data.split("_")[1]

        sql.execute('SELECT * FROM pizza WHERE number = ?', (number,))
        data = sql.fetchone()
        number = data[0]; pizza = data[1]; small = data[2]; medium = data[3]; big = data[4]; description = data[5]

        sql.execute('UPDATE user_action SET dough = ? WHERE id = ?', ("Тонкое", user_id))
        db.commit()

        sql.execute('SELECT * FROM user_action WHERE id = ?', (call.message.chat.id,))
        data = sql.fetchone()
        pizza = data[1]; size = data[2]; dough = data[3]; count = data[4]; price = data[5]; description = data[6]

        result = price * count
        total = "{: ,}".format(result).replace(",", " ")

        inline = types.InlineKeyboardMarkup()
        inline.row(types.InlineKeyboardButton(text = f"{'✅ Маленькая' if size == 'маленькая' else 'Маленькая'}", callback_data = f"small_{number}"),
                   types.InlineKeyboardButton(text = f"{'✅ Средняя' if size == 'средняя' else 'Средняя'}", callback_data = f"medium_{number}"),
                   types.InlineKeyboardButton(text = f"{'✅ Большая' if size == 'большая' else 'Большая'}", callback_data = f"big_{number}"))
        inline.row(types.InlineKeyboardButton(text = f"{'✅ Тонкое' if dough == 'Тонкое' else 'Тонкое'}", callback_data = f"mediumthin_{number}"),
                   types.InlineKeyboardButton(text = f"{'✅ Воздушное' if dough == 'Воздушное' else 'Воздушное'}", callback_data = f"mediumair_{number}"))
        inline.row(types.InlineKeyboardButton(text = "➖", callback_data = f"mediumminus_{number}"),
                   types.InlineKeyboardButton(text = f"{count}", callback_data = f"add"),
                   types.InlineKeyboardButton(text = "➕", callback_data = f"mediumplus_{number}"))
        inline.row(types.InlineKeyboardButton(text = f"Хочу 😍", callback_data = f"add"))

        text = (
        f"{pizza} {size}"
        f"\n\nТесто: <b>{dough}</b>"
        f"\n\n{description}"
        f"\n\nЦена:<b>{total} сум</b>")

        with open(f"photo/{number}.jpg", "rb") as photo:
            bot.edit_message_media(
            media = telebot.types.InputMedia(
            type = 'photo',
            media = photo,
            caption = text,
            parse_mode ="html"),
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            reply_markup = inline)


    elif call.data.startswith("mediumair_"):
        number = call.data.split("_")[1]

        sql.execute('SELECT * FROM pizza WHERE number = ?', (number,))
        data = sql.fetchone()
        number = data[0]; pizza = data[1]; small = data[2]; medium = data[3]; big = data[4]; description = data[5]

        sql.execute('UPDATE user_action SET dough = ? WHERE id = ?', ("Воздушное", user_id))
        db.commit()

        sql.execute('SELECT * FROM user_action WHERE id = ?', (call.message.chat.id,))
        data = sql.fetchone()
        pizza = data[1]; size = data[2]; dough = data[3]; count = data[4]; price = data[5]; description = data[6]

        result = price * count
        total = "{: ,}".format(result).replace(",", " ")

        inline = types.InlineKeyboardMarkup()
        inline.row(types.InlineKeyboardButton(text = f"{'✅ Маленькая' if size == 'маленькая' else 'Маленькая'}", callback_data = f"small_{number}"),
                   types.InlineKeyboardButton(text = f"{'✅ Средняя' if size == 'средняя' else 'Средняя'}", callback_data = f"medium_{number}"),
                   types.InlineKeyboardButton(text = f"{'✅ Большая' if size == 'большая' else 'Большая'}", callback_data = f"big_{number}"))
        inline.row(types.InlineKeyboardButton(text = f"{'✅ Тонкое' if dough == 'Тонкое' else 'Тонкое'}", callback_data = f"mediumthin_{number}"),
                   types.InlineKeyboardButton(text = f"{'✅ Воздушное' if dough == 'Воздушное' else 'Воздушное'}", callback_data = f"mediumair_{number}"))
        inline.row(types.InlineKeyboardButton(text = "➖", callback_data = f"mediumminus_{number}"),
                   types.InlineKeyboardButton(text = f"{count}", callback_data = f"add"),
                   types.InlineKeyboardButton(text = "➕", callback_data = f"mediumplus_{number}"))
        inline.row(types.InlineKeyboardButton(text = f"Хочу 😍", callback_data = f"add"))

        text = (
        f"{pizza} {size}"
        f"\n\nТесто: <b>{dough}</b>"
        f"\n\n{description}"
        f"\n\nЦена:<b>{total} сум</b>")

        with open(f"photo/{number}.jpg", "rb") as photo:
            bot.edit_message_media(
            media = telebot.types.InputMedia(
            type = 'photo',
            media = photo,
            caption = text,
            parse_mode ="html"),
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            reply_markup = inline)





    #  BIG

    elif call.data.startswith("bigthin_"):
        number = call.data.split("_")[1]

        sql.execute('SELECT * FROM pizza WHERE number = ?', (number,))
        data = sql.fetchone()
        number = data[0]; pizza = data[1]; small = data[2]; medium = data[3]; big = data[4]; description = data[5]


        if small == "-":

            sql.execute('UPDATE user_action SET dough = ? WHERE id = ?', ("Тонкое", user_id))
            sql.execute('UPDATE user_action SET price = ? WHERE id = ?', (big, user_id))
            db.commit()

            sql.execute('SELECT * FROM user_action WHERE id = ?', (user_id,))
            data = sql.fetchone()
            pizza = data[1]; size = data[2]; dough = data[3]; count = data[4]; price = data[5]; description = data[6]

            result = price * count
            total = "{: ,}".format(result).replace(",", " ")

            inline = types.InlineKeyboardMarkup()
            inline.row(types.InlineKeyboardButton(text = f"{'✅ Большая' if size == 'большая' else 'Большая'}", callback_data = f"-"))
            inline.row(types.InlineKeyboardButton(text = f"{'✅ Тонкое' if dough == 'Тонкое' else 'Тонкое'}", callback_data = f"bigthin_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Воздушное' if dough == 'Воздушное' else 'Воздушное'}", callback_data = f"bigair_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Хот-дог борт' if dough == 'Хот-дог борт' else 'Хот-дог борт'}", callback_data = f"hotdog_{number}"))
            inline.row(types.InlineKeyboardButton(text = "➖", callback_data = f"bigminus_{number}"),
                       types.InlineKeyboardButton(text = f"{count}", callback_data = f"add"),
                       types.InlineKeyboardButton(text = "➕", callback_data = f"bigplus_{number}"))
            inline.row(types.InlineKeyboardButton(text = f"Хочу 😍", callback_data = f"add"))

        else:

            sql.execute('UPDATE user_action SET dough = ? WHERE id = ?', ("Тонкое", user_id))
            sql.execute('UPDATE user_action SET price = ? WHERE id = ?', (big, user_id))
            db.commit()

            sql.execute('SELECT * FROM user_action WHERE id = ?', (call.message.chat.id,))
            data = sql.fetchone()
            pizza = data[1]; size = data[2]; dough = data[3]; count = data[4]; price = data[5]; description = data[6]

            result = price * count
            total = "{: ,}".format(result).replace(",", " ")

            inline = types.InlineKeyboardMarkup()
            inline.row(types.InlineKeyboardButton(text = f"{'✅ Маленькая' if size == 'маленькая' else 'Маленькая'}", callback_data = f"small_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Средняя' if size == 'средняя' else 'Средняя'}", callback_data = f"medium_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Большая' if size == 'большая' else 'Большая'}", callback_data = f"big_{number}"))
            inline.row(types.InlineKeyboardButton(text = f"{'✅ Тонкое' if dough == 'Тонкое' else 'Тонкое'}", callback_data = f"bigthin_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Воздушное' if dough == 'Воздушное' else 'Воздушное'}", callback_data = f"bigair_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Хот-дог борт' if dough == 'Хот-дог борт' else 'Хот-дог борт'}", callback_data = f"hotdog_{number}"))
            inline.row(types.InlineKeyboardButton(text = "➖", callback_data = f"bigminus_{number}"),
                       types.InlineKeyboardButton(text = f"{count}", callback_data = f"add"),
                       types.InlineKeyboardButton(text = "➕", callback_data = f"bigplus_{number}"))
            inline.row(types.InlineKeyboardButton(text = f"Хочу 😍", callback_data = f"add"))

        text = (
        f"{pizza} {size}"
        f"\n\nТесто: <b>{dough}</b>"
        f"\n\n{description}"
        f"\n\nЦена:<b>{total} сум</b>")

        with open(f"photo/{number}.jpg", "rb") as photo:
            bot.edit_message_media(
            media = telebot.types.InputMedia(
            type = 'photo',
            media = photo,
            caption = text,
            parse_mode ="html"),
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            reply_markup = inline)


    elif call.data.startswith("bigair_"):
        number = call.data.split("_")[1]

        sql.execute('SELECT * FROM pizza WHERE number = ?', (number,))
        data = sql.fetchone()
        number = data[0]; pizza = data[1]; small = data[2]; medium = data[3]; big = data[4]; description = data[5]

        if small == "-":

            sql.execute('UPDATE user_action SET dough = ? WHERE id = ?', ("Воздушное", user_id))
            sql.execute('UPDATE user_action SET price = ? WHERE id = ?', (big, user_id))
            db.commit()

            sql.execute('SELECT * FROM user_action WHERE id = ?', (user_id,))
            data = sql.fetchone()
            pizza = data[1]; size = data[2]; dough = data[3]; count = data[4]; price = data[5]; description = data[6]

            result = price * count
            total = "{: ,}".format(result).replace(",", " ")

            inline = types.InlineKeyboardMarkup()
            inline.row(types.InlineKeyboardButton(text = f"{'✅ Большая' if size == 'большая' else 'Большая'}", callback_data = f"-"))
            inline.row(types.InlineKeyboardButton(text = f"{'✅ Тонкое' if dough == 'Тонкое' else 'Тонкое'}", callback_data = f"bigthin_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Воздушное' if dough == 'Воздушное' else 'Воздушное'}", callback_data = f"bigair_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Хот-дог борт' if dough == 'Хот-дог борт' else 'Хот-дог борт'}", callback_data = f"hotdog_{number}"))
            inline.row(types.InlineKeyboardButton(text = "➖", callback_data = f"bigminus_{number}"),
                       types.InlineKeyboardButton(text = f"{count}", callback_data = f"add"),
                       types.InlineKeyboardButton(text = "➕", callback_data = f"bigplus_{number}"))
            inline.row(types.InlineKeyboardButton(text = f"Хочу 😍", callback_data = f"add"))

        else:

            sql.execute('UPDATE user_action SET dough = ? WHERE id = ?', ("Воздушное", user_id))
            sql.execute('UPDATE user_action SET price = ? WHERE id = ?', (big, user_id))
            db.commit()

            sql.execute('SELECT * FROM user_action WHERE id = ?', (call.message.chat.id,))
            data = sql.fetchone()
            pizza = data[1]; size = data[2]; dough = data[3]; count = data[4]; price = data[5]; description = data[6]

            result = price * count
            total = "{: ,}".format(result).replace(",", " ")

            inline = types.InlineKeyboardMarkup()
            inline.row(types.InlineKeyboardButton(text = f"{'✅ Маленькая' if size == 'маленькая' else 'Маленькая'}", callback_data = f"small_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Средняя' if size == 'средняя' else 'Средняя'}", callback_data = f"medium_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Большая' if size == 'большая' else 'Большая'}", callback_data = f"big_{number}"))
            inline.row(types.InlineKeyboardButton(text = f"{'✅ Тонкое' if dough == 'Тонкое' else 'Тонкое'}", callback_data = f"bigthin_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Воздушное' if dough == 'Воздушное' else 'Воздушное'}", callback_data = f"bigair_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Хот-дог борт' if dough == 'Хот-дог борт' else 'Хот-дог борт'}", callback_data = f"hotdog_{number}"))
            inline.row(types.InlineKeyboardButton(text = "➖", callback_data = f"bigminus_{number}"),
                       types.InlineKeyboardButton(text = f"{count}", callback_data = f"add"),
                       types.InlineKeyboardButton(text = "➕", callback_data = f"bigplus_{number}"))
            inline.row(types.InlineKeyboardButton(text = f"Хочу 😍", callback_data = f"add"))

        text = (
        f"{pizza} {size}"
        f"\n\nТесто: <b>{dough}</b>"
        f"\n\n{description}"
        f"\n\nЦена:<b>{total} сум</b>")

        with open(f"photo/{number}.jpg", "rb") as photo:
            bot.edit_message_media(
            media = telebot.types.InputMedia(
            type = 'photo',
            media = photo,
            caption = text,
            parse_mode ="html"),
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            reply_markup = inline)


    elif call.data.startswith("hotdog_"):
        number = call.data.split("_")[1]

        sql.execute('SELECT * FROM pizza WHERE number = ?', (number,))
        data = sql.fetchone()
        number = data[0]; pizza = data[1]; small = data[2]; medium = data[3]; big = data[4]; description = data[5]

        if small == "-":

            sql.execute('UPDATE user_action SET dough = ? WHERE id = ?', ("Хот-дог борт", user_id))
            sql.execute('UPDATE user_action SET price = ? WHERE id = ?', (big + 20000, user_id))

            sql.execute('SELECT * FROM user_action WHERE id = ?', (user_id,))
            data = sql.fetchone()
            pizza = data[1]; size = data[2]; dough = data[3]; count = data[4]; price = data[5]; description = data[6]

            result = price * count
            total = "{: ,}".format(result).replace(",", " ")

            inline = types.InlineKeyboardMarkup()
            inline.row(types.InlineKeyboardButton(text = f"{'✅ Большая' if size == 'большая' else 'Большая'}", callback_data = f"-"))
            inline.row(types.InlineKeyboardButton(text = f"{'✅ Тонкое' if dough == 'Тонкое' else 'Тонкое'}", callback_data = f"bigthin_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Воздушное' if dough == 'Воздушное' else 'Воздушное'}", callback_data = f"bigair_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Хот-дог борт' if dough == 'Хот-дог борт' else 'Хот-дог борт'}", callback_data = f"hotdog_{number}"))
            inline.row(types.InlineKeyboardButton(text = "➖", callback_data = f"bigminus_{number}"),
                       types.InlineKeyboardButton(text = f"{count}", callback_data = f"add"),
                       types.InlineKeyboardButton(text = "➕", callback_data = f"bigplus_{number}"))
            inline.row(types.InlineKeyboardButton(text = f"Хочу 😍", callback_data = f"add"))

        else:

            sql.execute('UPDATE user_action SET dough = ? WHERE id = ?', ("Хот-дог борт", user_id))
            sql.execute('UPDATE user_action SET price = ? WHERE id = ?', (big + 20000, user_id))
            db.commit()

            sql.execute('SELECT * FROM user_action WHERE id = ?', (call.message.chat.id,))
            data = sql.fetchone()
            pizza = data[1]; size = data[2]; dough = data[3]; count = data[4]; price = data[5]; description = data[6]

            result = price * count
            total = "{: ,}".format(result).replace(",", " ")

            inline = types.InlineKeyboardMarkup()
            inline.row(types.InlineKeyboardButton(text = f"{'✅ Маленькая' if size == 'маленькая' else 'Маленькая'}", callback_data = f"small_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Средняя' if size == 'средняя' else 'Средняя'}", callback_data = f"medium_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Большая' if size == 'большая' else 'Большая'}", callback_data = f"big_{number}"))
            inline.row(types.InlineKeyboardButton(text = f"{'✅ Тонкое' if dough == 'Тонкое' else 'Тонкое'}", callback_data = f"bigthin_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Воздушное' if dough == 'Воздушное' else 'Воздушное'}", callback_data = f"bigair_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Хот-дог борт' if dough == 'Хот-дог борт' else 'Хот-дог борт'}", callback_data = f"hotdog_{number}"))
            inline.row(types.InlineKeyboardButton(text = "➖", callback_data = f"bigminus_{number}"),
                       types.InlineKeyboardButton(text = f"{count}", callback_data = f"add"),
                       types.InlineKeyboardButton(text = "➕", callback_data = f"bigplus_{number}"))
            inline.row(types.InlineKeyboardButton(text = f"Хочу 😍", callback_data = f"add"))

        text = (
        f"{pizza} {size}"
        f"\n\nТесто: <b>{dough}</b>"
        f"\n\n{description}"
        f"\n\nЦена:<b>{total} сум</b>")

        with open(f"photo/{number}.jpg", "rb") as photo:
            bot.edit_message_media(
            media = telebot.types.InputMedia(
            type = 'photo',
            media = photo,
            caption = text,
            parse_mode ="html"),
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            reply_markup = inline)





#  PLUS

    #  SMALL

    elif call.data.startswith("smallplus_"):
        number = call.data.split("_")[1]

        sql.execute('SELECT * FROM pizza WHERE number = ?', (number,))
        data = sql.fetchone()
        number = data[0]; pizza = data[1]; small = data[2]; medium = data[3]; big = data[4]; description = data[5]

        sql.execute('UPDATE user_action SET count = count + ? WHERE id = ?', (1, call.message.chat.id))
        db.commit()

        sql.execute('SELECT * FROM user_action WHERE id = ?', (call.message.chat.id,))
        data = sql.fetchone()
        pizza = data[1]; size = data[2]; dough = data[3]; count = data[4]; price = data[5]; description = data[6]

        result = price * count
        total = "{: ,}".format(result).replace(",", " ")

        inline = types.InlineKeyboardMarkup()
        inline.row(types.InlineKeyboardButton(text = f"{'✅ Маленькая' if size == 'маленькая' else 'Маленькая'}", callback_data = f"small_{number}"),
                   types.InlineKeyboardButton(text = f"{'✅ Средняя' if size == 'средняя' else 'Средняя'}", callback_data = f"medium_{number}"),
                   types.InlineKeyboardButton(text = f"{'✅ Большая' if size == 'большая' else 'Большая'}", callback_data = f"big_{number}"))
        inline.row(types.InlineKeyboardButton(text = f"{'✅ Воздушное' if dough == 'Воздушное' else 'Воздушное'}", callback_data = f"smallair_{number}"))
        inline.row(types.InlineKeyboardButton(text = "➖", callback_data = f"smallminus_{number}"),
                   types.InlineKeyboardButton(text = f"{count}", callback_data = f"add"),
                   types.InlineKeyboardButton(text = "➕", callback_data = f"smallplus_{number}"))
        inline.row(types.InlineKeyboardButton(text = f"Хочу 😍", callback_data = f"add"))

        text = (
        f"{pizza} {size}"
        f"\n\nТесто: <b>{dough}</b>"
        f"\n\n{description}"
        f"\n\nЦена:<b>{total} сум</b>")

        with open(f"photo/{number}.jpg", "rb") as photo:
            bot.edit_message_media(
            media = telebot.types.InputMedia(
            type = 'photo',
            media = photo,
            caption = text,
            parse_mode ="html"),
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            reply_markup = inline)

    #  MEDIUM

    elif call.data.startswith("mediumplus_"):
        number = call.data.split("_")[1]

        sql.execute('SELECT * FROM pizza WHERE number = ?', (number,))
        data = sql.fetchone()
        number = data[0]; pizza = data[1]; small = data[2]; medium = data[3]; big = data[4]; description = data[5]

        sql.execute('UPDATE user_action SET count = count + ? WHERE id = ?', (1, call.message.chat.id))
        db.commit()

        sql.execute('SELECT * FROM user_action WHERE id = ?', (call.message.chat.id,))
        data = sql.fetchone()
        pizza = data[1]; size = data[2]; dough = data[3]; count = data[4]; price = data[5]; description = data[6]

        result = price * count
        total = "{: ,}".format(result).replace(",", " ")

        inline = types.InlineKeyboardMarkup()
        inline.row(types.InlineKeyboardButton(text = f"{'✅ Маленькая' if size == 'маленькая' else 'Маленькая'}", callback_data = f"small_{number}"),
                   types.InlineKeyboardButton(text = f"{'✅ Средняя' if size == 'средняя' else 'Средняя'}", callback_data = f"medium_{number}"),
                   types.InlineKeyboardButton(text = f"{'✅ Большая' if size == 'большая' else 'Большая'}", callback_data = f"big_{number}"))
        inline.row(types.InlineKeyboardButton(text = f"{'✅ Тонкое' if dough == 'Тонкое' else 'Тонкое'}", callback_data = f"mediumthin_{number}"),
                   types.InlineKeyboardButton(text = f"{'✅ Воздушное' if dough == 'Воздушное' else 'Воздушное'}", callback_data = f"mediumair_{number}"))
        inline.row(types.InlineKeyboardButton(text = "➖", callback_data = f"mediumminus_{number}"),
                   types.InlineKeyboardButton(text = f"{count}", callback_data = f"add"),
                   types.InlineKeyboardButton(text = "➕", callback_data = f"mediumplus_{number}"))
        inline.row(types.InlineKeyboardButton(text = f"Хочу 😍", callback_data = f"add"))

        text = (
        f"{pizza} {size}"
        f"\n\nТесто: <b>{dough}</b>"
        f"\n\n{description}"
        f"\n\nЦена:<b>{total} сум</b>")

        with open(f"photo/{number}.jpg", "rb") as photo:
            bot.edit_message_media(
            media = telebot.types.InputMedia(
            type = 'photo',
            media = photo,
            caption = text,
            parse_mode ="html"),
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            reply_markup = inline)

    #  BIG

    elif call.data.startswith("bigplus_"):
        number = call.data.split("_")[1]

        sql.execute('SELECT * FROM pizza WHERE number = ?', (number,))
        data = sql.fetchone()
        number = data[0]; pizza = data[1]; small = data[2]; medium = data[3]; big = data[4]; description = data[5]

        if small == "-":

            sql.execute('UPDATE user_action SET count = count + ? WHERE id = ?', (1, call.message.chat.id))
            db.commit()

            sql.execute('SELECT * FROM user_action WHERE id = ?', (user_id,))
            data = sql.fetchone()
            pizza = data[1]; size = data[2]; dough = data[3]; count = data[4]; price = data[5]; description = data[6]

            result = price * count
            total = "{: ,}".format(result).replace(",", " ")

            inline = types.InlineKeyboardMarkup()
            inline.row(types.InlineKeyboardButton(text = f"{'✅ Большая' if size == 'большая' else 'Большая'}", callback_data = f"-"))
            inline.row(types.InlineKeyboardButton(text = f"{'✅ Тонкое' if dough == 'Тонкое' else 'Тонкое'}", callback_data = f"bigthin_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Воздушное' if dough == 'Воздушное' else 'Воздушное'}", callback_data = f"bigair_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Хот-дог борт' if dough == 'Хот-дог борт' else 'Хот-дог борт'}", callback_data = f"hotdog_{number}"))
            inline.row(types.InlineKeyboardButton(text = "➖", callback_data = f"bigminus_{number}"),
                       types.InlineKeyboardButton(text = f"{count}", callback_data = f"add"),
                       types.InlineKeyboardButton(text = "➕", callback_data = f"bigplus_{number}"))
            inline.row(types.InlineKeyboardButton(text = f"Хочу 😍", callback_data = f"add"))

        else:

            sql.execute('UPDATE user_action SET count = count + ? WHERE id = ?', (1, call.message.chat.id))
            db.commit()

            sql.execute('SELECT * FROM user_action WHERE id = ?', (call.message.chat.id,))
            data = sql.fetchone()
            pizza = data[1]; size = data[2]; dough = data[3]; count = data[4]; price = data[5]; description = data[6]

            result = price * count
            total = "{: ,}".format(result).replace(",", " ")

            inline = types.InlineKeyboardMarkup()
            inline.row(types.InlineKeyboardButton(text = f"{'✅ Маленькая' if size == 'маленькая' else 'Маленькая'}", callback_data = f"small_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Средняя' if size == 'средняя' else 'Средняя'}", callback_data = f"medium_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Большая' if size == 'большая' else 'Большая'}", callback_data = f"big_{number}"))
            inline.row(types.InlineKeyboardButton(text = f"{'✅ Тонкое' if dough == 'Тонкое' else 'Тонкое'}", callback_data = f"bigthin_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Воздушное' if dough == 'Воздушное' else 'Воздушное'}", callback_data = f"bigair_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Хот-дог борт' if dough == 'Хот-дог борт' else 'Хот-дог борт'}", callback_data = f"hotdog_{number}"))
            inline.row(types.InlineKeyboardButton(text = "➖", callback_data = f"bigminus_{number}"),
                       types.InlineKeyboardButton(text = f"{count}", callback_data = f"add"),
                       types.InlineKeyboardButton(text = "➕", callback_data = f"bigplus_{number}"))
            inline.row(types.InlineKeyboardButton(text = f"Хочу 😍", callback_data = f"add"))

        text = (
        f"{pizza} {size}"
        f"\n\nТесто: <b>{dough}</b>"
        f"\n\n{description}"
        f"\n\nЦена:<b>{total} сум</b>")

        with open(f"photo/{number}.jpg", "rb") as photo:
            bot.edit_message_media(
            media = telebot.types.InputMedia(
            type = 'photo',
            media = photo,
            caption = text,
            parse_mode ="html"),
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            reply_markup = inline)




#  MINUS

    #  SMALL

    elif call.data.startswith("smallminus_"):
        number = call.data.split("_")[1]

        sql.execute('SELECT * FROM pizza WHERE number = ?', (number,))
        data = sql.fetchone()
        number = data[0]; pizza = data[1]; small = data[2]; medium = data[3]; big = data[4]; description = data[5]

        sql.execute('UPDATE user_action SET count = count - ? WHERE id = ?', (1, call.message.chat.id))
        db.commit()

        sql.execute('SELECT * FROM user_action WHERE id = ?', (call.message.chat.id,))
        data = sql.fetchone()
        pizza = data[1]; size = data[2]; dough = data[3]; count = data[4]; price = data[5]; description = data[6]

        result = price * count
        total = "{: ,}".format(result).replace(",", " ")

        inline = types.InlineKeyboardMarkup()
        inline.row(types.InlineKeyboardButton(text = f"{'✅ Маленькая' if size == 'маленькая' else 'Маленькая'}", callback_data = f"small_{number}"),
                   types.InlineKeyboardButton(text = f"{'✅ Средняя' if size == 'средняя' else 'Средняя'}", callback_data = f"medium_{number}"),
                   types.InlineKeyboardButton(text = f"{'✅ Большая' if size == 'большая' else 'Большая'}", callback_data = f"big_{number}"))
        inline.row(types.InlineKeyboardButton(text = f"{'✅ Воздушное' if dough == 'Воздушное' else 'Воздушное'}", callback_data = f"smallair_{number}"))
        inline.row(types.InlineKeyboardButton(text = "➖", callback_data = f"smallminus_{number}"),
                   types.InlineKeyboardButton(text = f"{count}", callback_data = f"add"),
                   types.InlineKeyboardButton(text = "➕", callback_data = f"smallplus_{number}"))
        inline.row(types.InlineKeyboardButton(text = f"Хочу 😍", callback_data = f"add"))

        text = (
        f"{pizza} {size}"
        f"\n\nТесто: <b>{dough}</b>"
        f"\n\n{description}"
        f"\n\nЦена:<b>{total} сум</b>")

        with open(f"photo/{number}.jpg", "rb") as photo:
            bot.edit_message_media(
            media = telebot.types.InputMedia(
            type = 'photo',
            media = photo,
            caption = text,
            parse_mode ="html"),
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            reply_markup = inline)

    #  MEDIUM

    elif call.data.startswith("mediumminus_"):
        number = call.data.split("_")[1]

        sql.execute('SELECT * FROM pizza WHERE number = ?', (number,))
        data = sql.fetchone()
        number = data[0]; pizza = data[1]; small = data[2]; medium = data[3]; big = data[4]; description = data[5]

        sql.execute('UPDATE user_action SET count = count - ? WHERE id = ?', (1, call.message.chat.id))
        db.commit()

        sql.execute('SELECT * FROM user_action WHERE id = ?', (call.message.chat.id,))
        data = sql.fetchone()
        pizza = data[1]; size = data[2]; dough = data[3]; count = data[4]; price = data[5]; description = data[6]

        result = price * count
        total = "{: ,}".format(result).replace(",", " ")

        inline = types.InlineKeyboardMarkup()
        inline.row(types.InlineKeyboardButton(text = f"{'✅ Маленькая' if size == 'маленькая' else 'Маленькая'}", callback_data = f"small_{number}"),
                   types.InlineKeyboardButton(text = f"{'✅ Средняя' if size == 'средняя' else 'Средняя'}", callback_data = f"medium_{number}"),
                   types.InlineKeyboardButton(text = f"{'✅ Большая' if size == 'большая' else 'Большая'}", callback_data = f"big_{number}"))
        inline.row(types.InlineKeyboardButton(text = f"{'✅ Тонкое' if dough == 'Тонкое' else 'Тонкое'}", callback_data = f"mediumthin_{number}"),
                   types.InlineKeyboardButton(text = f"{'✅ Воздушное' if dough == 'Воздушное' else 'Воздушное'}", callback_data = f"mediumair_{number}"))
        inline.row(types.InlineKeyboardButton(text = "➖", callback_data = f"mediumminus_{number}"),
                   types.InlineKeyboardButton(text = f"{count}", callback_data = f"add"),
                   types.InlineKeyboardButton(text = "➕", callback_data = f"mediumplus_{number}"))
        inline.row(types.InlineKeyboardButton(text = f"Хочу 😍", callback_data = f"add"))

        text = (
        f"{pizza} {size}"
        f"\n\nТесто: <b>{dough}</b>"
        f"\n\n{description}"
        f"\n\nЦена:<b>{total} сум</b>")

        with open(f"photo/{number}.jpg", "rb") as photo:
            bot.edit_message_media(
            media = telebot.types.InputMedia(
            type = 'photo',
            media = photo,
            caption = text,
            parse_mode ="html"),
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            reply_markup = inline)

    #  BIG

    elif call.data.startswith("bigminus_"):
        number = call.data.split("_")[1]

        sql.execute('SELECT * FROM pizza WHERE number = ?', (number,))
        data = sql.fetchone()
        number = data[0]; pizza = data[1]; small = data[2]; medium = data[3]; big = data[4]; description = data[5]

        if small == "-":

            sql.execute('UPDATE user_action SET count = count - ? WHERE id = ?', (1, call.message.chat.id))
            db.commit()

            sql.execute('SELECT * FROM user_action WHERE id = ?', (user_id,))
            data = sql.fetchone()
            pizza = data[1]; size = data[2]; dough = data[3]; count = data[4]; price = data[5]; description = data[6]

            result = price * count
            total = "{: ,}".format(result).replace(",", " ")


            inline = types.InlineKeyboardMarkup()
            inline.row(types.InlineKeyboardButton(text = f"{'✅ Большая' if size == 'большая' else 'Большая'}", callback_data = f"-"))
            inline.row(types.InlineKeyboardButton(text = f"{'✅ Тонкое' if dough == 'Тонкое' else 'Тонкое'}", callback_data = f"bigthin_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Воздушное' if dough == 'Воздушное' else 'Воздушное'}", callback_data = f"bigair_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Хот-дог борт' if dough == 'Хот-дог борт' else 'Хот-дог борт'}", callback_data = f"hotdog_{number}"))
            inline.row(types.InlineKeyboardButton(text = "➖", callback_data = f"bigminus_{number}"),
                       types.InlineKeyboardButton(text = f"{count}", callback_data = f"add"),
                       types.InlineKeyboardButton(text = "➕", callback_data = f"bigplus_{number}"))
            inline.row(types.InlineKeyboardButton(text = f"Хочу 😍", callback_data = f"add"))

        else:

            sql.execute('UPDATE user_action SET count = count - ? WHERE id = ?', (1, call.message.chat.id))
            db.commit()

            sql.execute('SELECT * FROM user_action WHERE id = ?', (call.message.chat.id,))
            data = sql.fetchone()
            pizza = data[1]; size = data[2]; dough = data[3]; count = data[4]; price = data[5]; description = data[6]

            result = price * count
            total = "{: ,}".format(result).replace(",", " ")


            inline = types.InlineKeyboardMarkup()
            inline.row(types.InlineKeyboardButton(text = f"{'✅ Маленькая' if size == 'маленькая' else 'Маленькая'}", callback_data = f"small_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Средняя' if size == 'средняя' else 'Средняя'}", callback_data = f"medium_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Большая' if size == 'большая' else 'Большая'}", callback_data = f"big_{number}"))
            inline.row(types.InlineKeyboardButton(text = f"{'✅ Тонкое' if dough == 'Тонкое' else 'Тонкое'}", callback_data = f"bigthin_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Воздушное' if dough == 'Воздушное' else 'Воздушное'}", callback_data = f"bigair_{number}"),
                       types.InlineKeyboardButton(text = f"{'✅ Хот-дог борт' if dough == 'Хот-дог борт' else 'Хот-дог борт'}", callback_data = f"hotdog_{number}"))
            inline.row(types.InlineKeyboardButton(text = "➖", callback_data = f"bigminus_{number}"),
                       types.InlineKeyboardButton(text = f"{count}", callback_data = f"add"),
                       types.InlineKeyboardButton(text = "➕", callback_data = f"bigplus_{number}"))
            inline.row(types.InlineKeyboardButton(text = f"Хочу 😍", callback_data = f"add"))


        text = (
        f"{pizza} {size}"
        f"\n\nТесто: <b>{dough}</b>"
        f"\n\n{description}"
        f"\n\nЦена:<b>{total} сум</b>")

        with open(f"photo/{number}.jpg", "rb") as photo:
            bot.edit_message_media(
            media = telebot.types.InputMedia(
            type = 'photo',
            media = photo,
            caption = text,
            parse_mode ="html"),
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            reply_markup = inline)





    #  ADD TO CART

    elif call.data == "add":

        sql.execute('SELECT id FROM user_access WHERE id = ?', (call.message.chat.id,))
        user_id = sql.fetchone()[0]

        sql.execute('SELECT * FROM user_action WHERE id = ?', (call.message.chat.id,))
        data = sql.fetchone()
        pizza = data[1]; size = data[2]; dough = data[3]; count = data[4]; price = data[5]; description = data[6]

        sql.execute(f'INSERT INTO cart_{user_id} (pizza, size, dough, count, price, description) VALUES (?, ?, ?, ?, ?, ?)',
        (pizza, size, dough, count, price, description))
        db.commit()

        bot.send_message(user_id, f"Товар {pizza} успешно добавлен в корзину 📥 Закажем что-нибудь еще?", reply_markup=reply_markups.pizza_button)
        bot.send_message(user_id, "Выберите пиццу 🍕", parse_mode = "html", reply_markup = reply_markups.pizza_button)

        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.delete_message(call.message.chat.id, call.message.message_id - 1)





    #  EDIT CART

    elif call.data == "edit_cart":

        bot.delete_message(call.message.chat.id, call.message.message_id)

        sql.execute(f'SELECT * FROM cart_{user_id}')
        data = sql.fetchall()

        for row in data:
            number = row[0]
            pizza = row[1]
            size = row[2]
            count = row[4]
            price = row[5]

            if count == 1:

                inline = types.InlineKeyboardMarkup()
                inline.row(types.InlineKeyboardButton(text = "❌", callback_data = f"delete_{number}"),
                           types.InlineKeyboardButton(text = f"{count}", callback_data = "-"),
                           types.InlineKeyboardButton(text = "➕", callback_data = f"plus_{number}"))

            else:

                inline = types.InlineKeyboardMarkup()
                inline.row(types.InlineKeyboardButton(text = "➖", callback_data = f"minus_{number}"),
                           types.InlineKeyboardButton(text = f"{count}", callback_data = "-"),
                           types.InlineKeyboardButton(text = "➕", callback_data = f"plus_{number}"))

            bot.send_message(user_id, f"<b>{pizza} {size}</b>\n{count} x {price} = {count * price}", parse_mode="html", reply_markup = inline)





    #  MINUS CART

    elif call.data.startswith("minus_"):
        number = call.data.split("_")[1]

        try:

            sql.execute(f'UPDATE cart_{user_id} SET count = count - ? WHERE number = ?', (1, number))
            db.commit()

            sql.execute(f'SELECT * FROM cart_{user_id} WHERE number = ?', (number,))
            data = sql.fetchone()
            pizza = data[1]; size = data[2]; count = data[4]; price = data[5]

            if count == 1:

                inline = types.InlineKeyboardMarkup()
                inline.row(types.InlineKeyboardButton(text = "❌", callback_data = f"delete_{number}"),
                        types.InlineKeyboardButton(text = f"{count}", callback_data = "-"),
                        types.InlineKeyboardButton(text = "➕", callback_data = f"plus_{number}"))

            else:

                inline = types.InlineKeyboardMarkup()
                inline.row(types.InlineKeyboardButton(text = "➖", callback_data = f"minus_{number}"),
                        types.InlineKeyboardButton(text = f"{count}", callback_data = "-"),
                        types.InlineKeyboardButton(text = "➕", callback_data = f"plus_{number}"))

            bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = f"<b>{pizza} {size}</b>\n{count} x {price} = {price * count}", parse_mode = "html", reply_markup = inline)

        except:

            bot.delete_message(call.message.chat.id, call.message.message_id)



    #  PLUS CART

    elif call.data.startswith("plus_"):
        number = call.data.split("_")[1]

        try:

            sql.execute(f'UPDATE cart_{user_id} SET count = count + ? WHERE number = ?', (1, number))
            db.commit()

            sql.execute(f'SELECT * FROM cart_{user_id} WHERE number = ?', (number,))
            data = sql.fetchone()
            pizza = data[1]; size = data[2]; count = data[4]; price = data[5]

            if count == 1:

                inline = types.InlineKeyboardMarkup()
                inline.row(types.InlineKeyboardButton(text = "❌", callback_data = f"delete_{number}"),
                           types.InlineKeyboardButton(text = f"{count}", callback_data = "-"),
                           types.InlineKeyboardButton(text = "➕", callback_data = f"plus_{number}"))

            else:

                inline = types.InlineKeyboardMarkup()
                inline.row(types.InlineKeyboardButton(text = "➖", callback_data = f"minus_{number}"),
                           types.InlineKeyboardButton(text = f"{count}", callback_data = "-"),
                           types.InlineKeyboardButton(text = "➕", callback_data = f"plus_{number}"))

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = f"<b>{pizza} {size}</b>\n{count} x {price} = {price * count}", parse_mode = "html", reply_markup = inline)

        except:

            bot.delete_message(call.message.chat.id, call.message.message_id)



    #  DELETE CART

    elif call.data.startswith("delete_"):
        number = call.data.split("_")[1]

        bot.delete_message(call.message.chat.id, call.message.message_id)

        try:

            sql.execute(f'DELETE FROM cart_{user_id} WHERE number = ?', (number,))
            db.commit()

        except:

            pass


















# #  DISLAY SMALL

# def display_small(call):

#     sql.execute('SELECT * FROM user_action WHERE id = ?', (call.message.chat.id,))
#     data = sql.fetchone()
#     pizza = data[1]; size = data[2]; dough = data[3]; count = data[4]; price = data[5]; description = data[6]

#     inline = types.InlineKeyboardMarkup()
#     inline.row(types.InlineKeyboardButton(text = f"{'✅ Маленькая' if size == 'маленькая' else 'Маленькая'}", callback_data = "small"),
#                types.InlineKeyboardButton(text = f"{'✅ Средняя' if size == 'средняя' else 'Средняя'}", callback_data = "medium"),
#                types.InlineKeyboardButton(text = f"{'✅ Большая' if size == 'большая' else 'Большая'}", callback_data = "big"))
#     inline.row(types.InlineKeyboardButton(text = f"{'✅ Воздушное' if dough == 'Воздушное' else 'Воздушное'}", callback_data = "air"))
#     inline.row(types.InlineKeyboardButton(text = "➖", callback_data = "small_minus"),
#                types.InlineKeyboardButton(text = f"{count}", callback_data = "add"),
#                types.InlineKeyboardButton(text = "➕", callback_data = "small_plus"))
#     inline.row(types.InlineKeyboardButton(text = f"Хочу 😍", callback_data = "add"))

#     text = (
#     f"{pizza} {size}"
#     f"\n\nТесто: <b>{dough}</b>"
#     f"\n\n{description}"
#     f"\n\nЦена: <b>{price * count} сум</b>")

#     with open("photo/pizza_1.jpg", "rb") as photo:
#         bot.edit_message_media(
#         media = telebot.types.InputMedia(
#         type = 'photo',
#         media = photo,
#         caption = text,
#         parse_mode ="html"),
#         chat_id = call.message.chat.id,
#         message_id = call.message.message_id,
#         reply_markup = inline)




# #  DISPLAY MEDIUM

# def display_medium(call):

#     sql.execute('SELECT * FROM user_action WHERE id = ?', (call.message.chat.id,))
#     data = sql.fetchone()
#     pizza = data[1]; size = data[2]; dough = data[3]; count = data[4]; price = data[5]; description = data[6]

#     inline = types.InlineKeyboardMarkup()
#     inline.row(types.InlineKeyboardButton(text = f"{'✅ Маленькая' if size == 'маленькая' else 'Маленькая'}", callback_data = "small"),
#                types.InlineKeyboardButton(text = f"{'✅ Средняя' if size == 'средняя' else 'Средняя'}", callback_data = "medium"),
#                types.InlineKeyboardButton(text = f"{'✅ Большая' if size == 'большая' else 'Большая'}", callback_data = "big"))
#     inline.row(types.InlineKeyboardButton(text = f"{'✅ Тонкое' if dough == 'Тонкое' else 'Тонкое'}", callback_data = "medium_thin"),
#                types.InlineKeyboardButton(text = f"{'✅ Воздушное' if dough == 'Воздушное' else 'Воздушное'}", callback_data = "medium_air"))
#     inline.row(types.InlineKeyboardButton(text = "➖", callback_data = "medium_minus"),
#                types.InlineKeyboardButton(text = f"{count}", callback_data = "add"),
#                types.InlineKeyboardButton(text = "➕", callback_data = "medium_plus"))
#     inline.row(types.InlineKeyboardButton(text = f"Хочу 😍", callback_data = "add"))

#     text = (
#     f"{pizza} {size}"
#     f"\n\nТесто: <b>{dough}</b>"
#     f"\n\n{description}"
#     f"\n\nЦена: <b>{price * count} сум</b>")

#     with open("photo/pizza_1.jpg", "rb") as photo:
#         bot.edit_message_media(
#         media = telebot.types.InputMedia(
#         type = 'photo',
#         media = photo,
#         caption = text,
#         parse_mode ="html"),
#         chat_id = call.message.chat.id,
#         message_id = call.message.message_id,
#         reply_markup = inline)



# #  DISPLAY BIG

# def display_big(call):

#     sql.execute('SELECT * FROM user_action WHERE id = ?', (call.message.chat.id,))
#     data = sql.fetchone()
#     pizza = data[1]; size = data[2]; dough = data[3]; count = data[4]; price = data[5]; description = data[6]

#     inline = types.InlineKeyboardMarkup()
#     inline.row(types.InlineKeyboardButton(text = f"{'✅ Маленькая' if size == 'маленькая' else 'Маленькая'}", callback_data = "small"),
#                types.InlineKeyboardButton(text = f"{'✅ Средняя' if size == 'средняя' else 'Средняя'}", callback_data = "medium"),
#                types.InlineKeyboardButton(text = f"{'✅ Большая' if size == 'большая' else 'Большая'}", callback_data = "big"))
#     inline.row(types.InlineKeyboardButton(text = f"{'✅ Тонкое' if dough == 'Тонкое' else 'Тонкое'}", callback_data = "big_thin"),
#                types.InlineKeyboardButton(text = f"{'✅ Воздушное' if dough == 'Воздушное' else 'Воздушное'}", callback_data = "big_air"),
#                types.InlineKeyboardButton(text = f"{'✅ Хот-дог борт' if dough == 'Хот-дог борт' else 'Хот-дог борт'}", callback_data = "big_hotdog"))
#     inline.row(types.InlineKeyboardButton(text = "➖", callback_data = "big_minus"),
#                types.InlineKeyboardButton(text = f"{count}", callback_data = "add"),
#                types.InlineKeyboardButton(text = "➕", callback_data = "big_plus"))
#     inline.row(types.InlineKeyboardButton(text = f"Хочу 😍", callback_data = "add"))

#     text = (
#     f"{pizza} {size}"
#     f"\n\nТесто: <b>{dough}</b>"
#     f"\n\n{description}"
#     f"\n\nЦена: <b>{price * count} сум</b>")

#     with open("photo/pizza_1.jpg", "rb") as photo:
#         bot.edit_message_media(
#         media = telebot.types.InputMedia(
#         type = 'photo',
#         media = photo,
#         caption = text,
#         parse_mode ="html"),
#         chat_id = call.message.chat.id,
#         message_id = call.message.message_id,
#         reply_markup = inline)




















    #  EDIT INLINE TEXT

    if call.data == "edit_inline":
        bot.edit_message_text(call.message.chat.id, call.message.message_id, text = "<b> ТЕКСТ </b>", parse_mode = "html", reply_markup = None)

    #  EDIT INLINE PHOTO

    if call.data == "edit_photo":
        with open("photo/photo.jpg", "rb") as photo:
            bot.edit_message_media( media = telebot.types.InputMedia(
                                    type = 'photo',
                                    media = photo,
                                    chat_id = call.message.chat.id,
                                    message_id = call.message.message_id,
                                    caption = "ТЕКСТ",
                                    parse_mode ="html"),
                                    reply_markup = None)

    #  DELETE INLINE  #

    if call.data == "delete_inline":
        bot.delete_message(call.message.chat.id, call.message.message_id)





#  LAUNCH THE BOT  #

if __name__=='__main__':

    while True:

        try:

            bot.polling(non_stop=True, interval=0)

        except Exception as e:

            print(e)

            time.sleep(5)

            continue