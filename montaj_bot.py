from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import os

BOT_TOKEN = "YOUR_BOT_TOKEN"

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

PTZ_PRICE = 6000
SD_PRICES = {"64gb": 800, "128gb": 1200, "256gb": 2000}
INSTALL_PTZ = 2000
STARTUP_PTZ = 2500
CABLE_PTZ = 65

pdfmetrics.registerFont(TTFont("DejaVu", "DejaVuSans.ttf"))

user_state = {}

def generate_pdf(user_id: int, content: str) -> str:
    filename = f"kom_predlozhenie_{user_id}.pdf"
    c = canvas.Canvas(filename)
    c.setFont("DejaVu", 12)
    y = 800
    for line in content.split('\n'):
        c.drawString(50, y, line)
        y -= 20
    c.save()
    return filename

async def send_estimate(update: Update, context: ContextTypes.DEFAULT_TYPE, msg: str):
    user_id = update.callback_query.from_user.id
    await update.callback_query.message.reply_text(msg)

    pdf_path = generate_pdf(user_id, msg)
    with open(pdf_path, "rb") as pdf_file:
        await context.bot.send_document(chat_id=user_id, document=InputFile(pdf_file), filename="Коммерческое_предложение.pdf")

    keyboard = [
        [InlineKeyboardButton("Начать сначала", callback_data="restart")]
    ]
    await update.callback_query.message.reply_text("Хотите начать заново?", reply_markup=InlineKeyboardMarkup(keyboard))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("IP-камеры", callback_data="ip")],
        [InlineKeyboardButton("PTZ-камеры", callback_data="ptz")]
    ]
    user_state[update.effective_user.id] = {}
    if update.message:
        await update.message.reply_text("Выберите тип системы:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text("Выберите тип системы:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "restart":
        await start(update, context)
        return

    if query.data == "ip":
        user_state[user_id] = {"type": "ip"}
        keyboard = [
            [InlineKeyboardButton("2 Мп", callback_data="2mp")],
            [InlineKeyboardButton("4 Мп", callback_data="4mp")],
            [InlineKeyboardButton("5 Мп", callback_data="5mp")],
        ]
        await query.edit_message_text("Выберите разрешение камер:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data in CAMERA_PRICES:
        state = user_state.get(user_id, {})
        state["resolution"] = query.data
        await query.edit_message_text("Сколько камер планируется установить?")

    elif query.data in HDD_PRICES:
        user_state[user_id]["hdd"] = query.data
        await query.edit_message_text("Сколько 8-портовых PoE-коммутаторов нужно установить?")

    elif query.data in SD_PRICES:
        user_state[user_id]["sdcard"] = query.data
        await query.edit_message_text("Примерное количество метров кабеля?")

    elif query.data == "ptz":
        user_state[user_id] = {"type": "ptz"}
        await query.edit_message_text("Сколько PTZ-камер планируется установить?")

    elif query.data == "final":
        state = user_state.get(user_id, {})
        if state.get("type") == "ptz":
            count = state["camera_count"]
            sd = state["sdcard"]
            cable = state["cable"]

            cam_total = count * PTZ_PRICE
            sd_total = count * SD_PRICES[sd]
            cable_total = cable * CABLE_PTZ
            install_total = count * INSTALL_PTZ + cable * INSTALL_CABLE + STARTUP_PTZ
            grand_total = cam_total + sd_total + cable_total + install_total

            msg = (
                f"Смета оборудования (PTZ):\n"
                f"Камеры {count} × {PTZ_PRICE}₽ = {cam_total}₽\n"
                f"SD-карта {sd} × {count} = {sd_total}₽\n"
                f"Кабель {cable} м × {CABLE_PTZ}₽ = {cable_total}₽\n"
                f"ИТОГО оборудование: {cam_total + sd_total + cable_total}₽\n\n"
                f"Монтажные работы:\n"
                f"Установка камер: {count} × {INSTALL_PTZ}₽ = {count * INSTALL_PTZ}₽\n"
                f"Прокладка кабеля: {cable} × {INSTALL_CABLE}₽ = {cable * INSTALL_CABLE}₽\n"
                f"Пусконаладочные: {STARTUP_PTZ}₽\n"
                f"ИТОГО монтаж: {install_total}₽\n\n"
                f"ИТОГО ОБЩЕЕ: {grand_total}₽"
            )
        else:
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

            install_total = (
                cam_count * INSTALL_CAMERA +
                INSTALL_SWITCH * switches +
                cable * INSTALL_CABLE +
                CONFIG_DVR +
                STARTUP_WORK
            )

            equipment_total = cameras_total + reg_price + hdd_price + switches_total + cable_total
            grand_total = equipment_total + install_total

            msg = (
                f"Смета оборудования:\n"
                f"Камеры {cam_count} × {cam_price}₽ = {cameras_total}₽\n"
                f"Видеорегистратор = {reg_price}₽\n"
                f"HDD {hdd} = {hdd_price}₽\n"
                f"PoE-коммутаторы {switches} × {POE_PRICE}₽ = {switches_total}₽\n"
                f"Кабель {cable} м × {CABLE_PRICE}₽ = {cable_total}₽\n"
                f"ИТОГО оборудование: {equipment_total}₽\n\n"
                f"Монтажные работы:\n"
                f"Установка камер: {cam_count} × {INSTALL_CAMERA}₽ = {cam_count * INSTALL_CAMERA}₽\n"
                f"Настройка регистратора: {CONFIG_DVR}₽\n"
                f"Пусконаладочные: {STARTUP_WORK}₽\n"
                f"Прокладка кабеля: {cable} × {INSTALL_CABLE}₽ = {cable * INSTALL_CABLE}₽\n"
                f"Установка коммутаторов: {switches} × {INSTALL_SWITCH}₽ = {switches * INSTALL_SWITCH}₽\n"
                f"ИТОГО монтаж: {install_total}₽\n\n"
                f"ИТОГО ОБЩЕЕ: {grand_total}₽"
            )

        await send_estimate(update, context, msg)
        user_state.pop(user_id, None)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    state = user_state.get(user_id, {})

    try:
        value = int(update.message.text)

        if state.get("type") == "ptz":
            if "camera_count" not in state:
                state["camera_count"] = value
                keyboard = [[InlineKeyboardButton(k.upper(), callback_data=k)] for k in SD_PRICES]
                await update.message.reply_text("Выберите SD-карту:", reply_markup=InlineKeyboardMarkup(keyboard))
            elif "sdcard" in state and "cable" not in state:
                state["cable"] = value
                keyboard = [[InlineKeyboardButton("Показать расчёт", callback_data="final")]]
                await update.message.reply_text("Нажмите, чтобы увидеть расчёт:", reply_markup=InlineKeyboardMarkup(keyboard))

        elif state.get("type") == "ip":
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
