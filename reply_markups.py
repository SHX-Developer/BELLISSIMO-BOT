from telebot.types import ReplyKeyboardMarkup, KeyboardButton



language_button = ReplyKeyboardMarkup(resize_keyboard = True)
language_button.row("🇺🇿 O'zbekcha", "🇷🇺 Русский")

contact_button = ReplyKeyboardMarkup(resize_keyboard = True)
contact_button.row(KeyboardButton(text="📱 Мой номер", request_contact=True))
contact_button.row(KeyboardButton(text="⬅️ Назад"))

city_button = ReplyKeyboardMarkup(resize_keyboard = True)
city_button.row("Ташкент", "Самарканд")
city_button.row("Андижан", "Коканд")
city_button.row("Фергана", "Чирчик")
city_button.row("Наманган", "Бухара")
city_button.row("Алмалык", "Нурафшон")

menu_button = ReplyKeyboardMarkup(resize_keyboard = True)
menu_button.row("🛍 Заказать")
menu_button.row("📖 Мои заказы", "🍕 Наши филиалы")
menu_button.row("☎️ Обратная связь", "⚙️ Настройки")

order_type_button = ReplyKeyboardMarkup(resize_keyboard = True)
order_type_button.row("🚙 Доставка", "🏃 Самовывоз")
order_type_button.row("⬅️ Назад")

order_delivery_button = ReplyKeyboardMarkup(resize_keyboard = True)
order_delivery_button.row("📍 Определить ближайщий филиал")
order_delivery_button.row("🗺 Мои адреса")
order_delivery_button.row("")

category_button = ReplyKeyboardMarkup(resize_keyboard = True)
category_button.row("⬅️ Назад", "💥 Акции", "📥 Корзина")
category_button.row("🍕 Пицца", "🥤 Напитки")
category_button.row("🔥 Горячие закуски", "🥗 Салаты")
category_button.row("🍰 Десерты", "⚪️ Соусы")

pizza_button = ReplyKeyboardMarkup(resize_keyboard = True)
pizza_button.row("⬅️ Назад", "📥 Корзина")
pizza_button.row("Куриный донар", "Сырная пицца")
pizza_button.row("Мясной микс", "Донар пицца")
pizza_button.row("Супер микс", "Сырный цыплёнок")
pizza_button.row("Двойная пепперони", "Цыплёнок ранч")
pizza_button.row("Халапенью", "Пепперони")
pizza_button.row("Мексиканская", "Маргарита")
pizza_button.row("Курица-барбекю", "Курица с грибами")
pizza_button.row("Комбо", "Кебаб")
pizza_button.row("Дабл Чизбургер", "Гавайская")
pizza_button.row("Вегетарианская", "Беллиссимо")
pizza_button.row("Альфредо")


action_button = ReplyKeyboardMarkup(resize_keyboard = True)
action_button.row("Хочу 😍")
action_button.row("⬅️  Назад")



cart_button = ReplyKeyboardMarkup(resize_keyboard = True)
cart_button.row("⬅️ Назад", "➡️ Продолжить")
cart_button.row("🎟 Промокод", "🔄 Очистить")

