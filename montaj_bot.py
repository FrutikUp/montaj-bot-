from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

PRICES = {
    "ip_inside": 1600,
    "ip_outside": 1800,
    "ahd_inside": 1500,
    "ahd_outside": 1700,
    "cable_m": 50,
    "cable_gofra": 80,
    "cable_kanal": 50,
    "recorder_4ch": 2500,
    "recorder_8ch": 3500,
    "recorder_16ch": 4500,
    "recorder_32ch": 5500,
    "recorder_64ch": 6500,
    "router": 1000,
    "hdd_1tb": 4500,
    "hdd_2tb": 6000,
    "hdd_4tb": 9000,
    "hdd_6tb": 12000,
}

CAMERA_PRICES = {
    "ip": {"2mp": 3000, "4mp": 4200, "5mp": 5500},
    "ahd": {"2mp": 2500, "4mp": 3400, "5mp": 4800},
}

user_state = {}

# Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Монтажные работы", callback_data='montage')],
        [InlineKeyboardButton("Собрать комплект оборудования", callback_data='equipment')],
    ]
    await update.message.reply_text("Выберите раздел:", reply_markup=InlineKeyboardMarkup(keyboard))

# Кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "montage":
        keyboard = [
            [InlineKeyboardButton("IP внутренняя", callback_data='ip_inside')],
            [InlineKeyboardButton("IP наружная", callback_data='ip_outside')],
            [InlineKeyboardButton("AHD внутренняя", callback_data='ahd_inside')],
            [InlineKeyboardButton("AHD наружная", callback_data='ahd_outside')],
        ]
        await query.edit_message_text("Выберите тип установки:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data in PRICES:
        user_state[user_id] = {"type": query.data}
        await query.edit_message_text("Сколько единиц нужно установить?")

    elif query.data == "equipment":
        keyboard = [
            [InlineKeyboardButton("IP-система", callback_data='eq_ip')],
            [InlineKeyboardButton("AHD-система", callback_data='eq_ahd')],
        ]
        await query.edit_message_text("Выберите тип системы:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data in ["eq_ip", "eq_ahd"]:
        user_state[user_id] = {"eq_type": query.data}
        keyboard = [
            [InlineKeyboardButton("2 Мп", callback_data="res_2mp")],
            [InlineKeyboardButton("4 Мп", callback_data="res_4mp")],
            [InlineKeyboardButton("5 Мп", callback_data="res_5mp")],
        ]
        await query.edit_message_text("Выберите разрешение камер:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("res_"):
        if user_id in user_state:
            user_state[user_id]["resolution"] = query.data.replace("res_", "")
            await query.edit_message_text("Сколько камер планируется установить?")

    elif query.data.startswith("recorder"):
        if user_id in user_state:
            user_state[user_id]["recorder"] = query.data
            await query.edit_message_text("Сколько метров кабеля необходимо?")

    elif query.data in ["hdd_1tb", "hdd_2tb", "hdd_4tb", "hdd_6tb"]:
        if user_id in user_state:
            user_state[user_id]["hdd"] = query.data
            await query.edit_message_text("Сколько метров кабеля нужно проложить?")

# Сообщения (ввод количества)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    state = user_state.get(user_id)

    if not state:
        await update.message.reply_text("Начните с команды /start.")
        return

    try:
        count = int(update.message.text)

        if "type" in state:
            price = PRICES[state["type"]]
            total = price * count
            await update.message.reply_text(f"Стоимость: {count} × {price}₽ = {total}₽")
            user_state.pop(user_id)

        elif "resolution" in state and "eq_type" in state and "camera_count" not in state:
            state["camera_count"] = count
            await update.message.reply_text("Сколько метров кабеля потребуется?")

        elif "camera_count" in state and "cable_meters" not in state:
            state["cable_meters"] = count
            await update.message.reply_text("Сколько метров гофры потребуется?")

        elif "cable_meters" in state and "gofra_meters" not in state:
            state["gofra_meters"] = count
            await update.message.reply_text("Сколько метров кабель-канала потребуется?")

        elif "gofra_meters" in state and "kanal_meters" not in state:
            state["kanal_meters"] = count
            keyboard = [
                [InlineKeyboardButton("HDD 1TB", callback_data="hdd_1tb")],
                [InlineKeyboardButton("HDD 2TB", callback_data="hdd_2tb")],
                [InlineKeyboardButton("HDD 4TB", callback_data="hdd_4tb")],
                [InlineKeyboardButton("HDD 6TB", callback_data="hdd_6tb")],
            ]
            await update.message.reply_text("Выберите объём HDD:", reply_markup=InlineKeyboardMarkup(keyboard))

        elif "kanal_meters" in state and "hdd" not in state:
            await update.message.reply_text("Выберите объём HDD для системы.")

    except ValueError:
        await update.message.reply_text("Введите число.")

# Запуск
def main():
    app = Application.builder().token("8157090611:AAF-tltFHeHE9r9LuCBMXS4UqsIt09SO7VE").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
