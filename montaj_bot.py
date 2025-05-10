from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

PRICES = {
    "ip_inside": 1600,
    "ip_outside": 1800,
    "ahd_inside": 1500,
    "ahd_outside": 1700,
    "cable_m": 50,
    "recorder": 5000,
    "hdd": 4000,
    "poe_switch": 3000,
    "power_supply": 500,
}

CAMERA_PRICES = {
    "ip": {"2mp": 3200, "4mp": 3700, "5mp": 4000},
    "ahd": {"2mp": 2500, "4mp": 3000, "5mp": 3300},
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

    elif query.data in ["poe", "psu"]:
        if user_id in user_state:
            state = user_state[user_id]
            state["power"] = query.data

            is_ip = state["eq_type"] == "eq_ip"
            resolution = state["resolution"]
            cam_count = state["camera_count"]
            cable_m = state["cable_meters"]

            cam_price = CAMERA_PRICES["ip" if is_ip else "ahd"][resolution]
            cameras_total = cam_count * cam_price
            cable_total = cable_m * PRICES["cable_m"]
            recorder = PRICES["recorder"]
            hdd = PRICES["hdd"]
            power = PRICES["poe_switch"] if state["power"] == "poe" else PRICES["power_supply"]
            power_total = power if state["power"] == "poe" else power * cam_count

            total = cameras_total + cable_total + recorder + hdd + power_total

            msg = (
                f"Система: {'IP' if is_ip else 'AHD'}\n"
                f"Камеры ({cam_count} шт, {resolution}): {cameras_total}₽\n"
                f"Кабель ({cable_m} м): {cable_total}₽\n"
                f"Регистратор: {recorder}₽\n"
                f"HDD: {hdd}₽\n"
                f"{'PoE-коммутатор' if state['power'] == 'poe' else 'Блоки питания'}: {power_total}₽\n"
                f"Итого: {total}₽"
            )
            await query.edit_message_text(msg)
            user_state.pop(user_id)

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
            await update.message.reply_text("Сколько метров кабеля понадобится (примерно)?")

        elif "camera_count" in state and "cable_meters" not in state:
            state["cable_meters"] = count
            keyboard = [
                [InlineKeyboardButton("PoE-коммутатор", callback_data="poe")],
                [InlineKeyboardButton("Блоки питания", callback_data="psu")],
            ]
            await update.message.reply_text("Выберите тип питания:", reply_markup=InlineKeyboardMarkup(keyboard))

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
