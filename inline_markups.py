from telebot import types




#  INLINE BUTTON  #

button_inline = types.InlineKeyboardMarkup(row_width=1)
button_1 = types.InlineKeyboardButton(text="button_1", callback_data="button_1")
button_2 = types.InlineKeyboardButton(text="button_2", callback_data="button_2")
button_3 = types.InlineKeyboardButton(text="button_3", callback_data="button_3")
button_inline.add(button_1, button_2, button_3)


edit_cart = types.InlineKeyboardMarkup()
edit_cart.row(types.InlineKeyboardButton(text="✏️ Изменить", callback_data="edit_cart"))

edit_address = types.InlineKeyboardMarkup()
edit_address.row(types.InlineKeyboardButton(text="✏️ Изменить", callback_data="edit_address"))
