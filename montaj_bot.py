from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8157090611:AAF-tltFHeHE9r9LuCBMXS4UqsIt09SO7VE"

CAMERA_PRICES = {"2mp": 2800, "4mp": 4100, "5mp": 6000}
REGISTRATOR_PRICES = {4: 5000, 8: 8000, 16: 12000, 32: 20000}
HDD_PRICES = {"1tb": 4000, "2tb": 5700, "4tb": 8000}
POE_PRICE = 2600
CABLE_PRICE = 65

INSTALL_CAMERA = 1800
CONFIG_DVR = 2500
STARTUP_WORK = 2000
INSTALL_CABLE = 50
INSTALL_SWITCH = 1000

user_state = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Продолжить", callback_data="continue")]]
    await update.message.reply_text("Добро пожаловать в калькулятор монтажных работ!", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "continue":
        keyboard = [[InlineKeyboardButton("IP-камеры", callback_data="ip")]]
        user_state[user_id] = {}
        await query.edit_message_text("Выберите тип системы:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "ip":
        keyboard = [
            [InlineKeyboardButton("2 Мп", callback_data="2mp")],
            [InlineKeyboardButton("4 Мп", callback_data="4mp")],
            [InlineKeyboardButton("5 Мп", callback_data="5mp")],
        ]
        await query.edit_message_text("Выберите разрешение камер:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data in CAMERA_PRICES:
        user_state[user_id]["resolution"] = query.data
        await query.edit_message_text("Сколько камер планируется установить?")

    elif query.data in HDD_PRICES:
        user_state[user_id]["hdd"] = query.data
        await query.edit_message_text("Сколько 8-портовых PoE-коммутаторов нужно установить?")

    elif query.data == "final":
        state = user_state.get(user_id, {})
        if not state:
            return

        resolution = state["resolution"]
        cam_count = state["camera_count"]
        hdd = state["hdd"]
        switches = state["switches"]
        cable = state["cable"]

        cam_price = CAMERA_PRICES[resolution]
        cameras_total = cam_price * cam_count

        for count in sorted(REGISTRATOR_PRICES.keys()):
            if cam_count <= count:
                reg_price = REGISTRATOR_PRICES[count]
                break
        else:
            reg_price = REGISTRATOR_PRICES[32]

        hdd_price = HDD_PRICES[hdd]
        switches_total = switches * POE_PRICE
        cable_total = cable * CABLE_PRICE

        # Монтаж
        install_total = (
            cam_count * INSTALL_CAMERA +
            INSTALL_SWITCH * switches +
            INSTALL_CABLE * cable +
            CONFIG_DVR +
            STARTUP_WORK
        )

        equipment_total = cameras_total + reg_price + hdd_price + switches_total + cable_total
        grand_total = equipment_total + install_total

        msg = (
            f"**Смета оборудования:**\n"
            f"Камеры {cam_count} × {cam_price}₽ = {cameras_total}₽\n"
            f"Видеорегистратор = {reg_price}₽\n"
            f"HDD {hdd} = {hdd_price}₽\n"
            f"PoE-коммутаторы {switches} × {POE_PRICE}₽ = {switches_total}₽\n"
            f"Кабель {cable} м × {CABLE_PRICE}₽ = {cable_total}₽\n"
            f"ИТОГО оборудование: {equipment_total}₽\n\n"
            f"**Монтажные работы:**\n"
            f"Установка камер: {cam_count} × {INSTALL_CAMERA}₽ = {cam_count * INSTALL_CAMERA}₽\n"
            f"Настройка регистратора: {CONFIG_DVR}₽\n"
            f"Пусконаладочные: {STARTUP_WORK}₽\n"
            f"Прокладка кабеля: {cable} × {INSTALL_CABLE}₽ = {cable * INSTALL_CABLE}₽\n"
            f"Установка коммутаторов: {switches} × {INSTALL_SWITCH}₽ = {switches * INSTALL_SWITCH}₽\n"
            f"ИТОГО монтаж: {install_total}₽\n\n"
            f"**ИТОГО ОБЩЕЕ: {grand_total}₽**"
        )

        keyboard = [[InlineKeyboardButton("Начать сначала", callback_data="continue")]]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
        user_state.pop(user_id)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    state = user_state.get(user_id, {})

    try:
        value = int(update.message.text)
        if "resolution" in state and "camera_count" not in state:
            state["camera_count"] = value
            keyboard = [[InlineKeyboardButton(txt.upper(), callback_data=txt)] for txt in HDD_PRICES]
            await update.message.reply_text("Выберите HDD:", reply_markup=InlineKeyboardMarkup(keyboard))
        elif "hdd" in state and "switches" not in state:
            state["switches"] = value
            await update.message.reply_text("Примерное количество метров кабеля?")
        elif "switches" in state and "cable" not in state:
            state["cable"] = value
            keyboard = [[InlineKeyboardButton("Показать расчёт", callback_data="final")]]
            await update.message.reply_text("Нажмите, чтобы увидеть расчёт:", reply_markup=InlineKeyboardMarkup(keyboard))
    except ValueError:
        await update.message.reply_text("Введите число.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
