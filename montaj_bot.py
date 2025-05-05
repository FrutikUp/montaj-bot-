
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from telegram import ReplyKeyboardMarkup

import os

TOKEN = os.getenv("BOT_TOKEN")

# Этапы разговора
(CHOOSE_SECTION, MONTAJ_CAMERAS, CABLE, GOFRA, KABELKANAL, DVR, ROUTER, KIT_CAMERAS, KIT_DVR, KIT_HDD) = range(10)

# Старт
async def start(update, context):
    reply_keyboard = [["Монтажные работы", "Готовый комплект камер"]]
    await update.message.reply_text(
        "Привет! Чем могу помочь?
Выбери один из вариантов.",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return CHOOSE_SECTION

# Выбор раздела
async def choose_section(update, context):
    text = update.message.text.lower()
    if "монтаж" in text:
        await update.message.reply_text("Сколько камер нужно установить?")
        return MONTAJ_CAMERAS
    elif "комплект" in text:
        await update.message.reply_text("Сколько камер в комплекте?")
        return KIT_CAMERAS
    else:
        await update.message.reply_text("Пожалуйста, выбери один из предложенных вариантов.")
        return CHOOSE_SECTION

# Монтажные работы
async def get_cameras(update, context):
    context.user_data['cameras'] = int(update.message.text)
    await update.message.reply_text("Сколько метров кабеля?")
    return CABLE

async def get_cable(update, context):
    context.user_data['cable'] = int(update.message.text)
    await update.message.reply_text("Сколько метров кабеля в гофре?")
    return GOFRA

async def get_gofra(update, context):
    context.user_data['gofra'] = int(update.message.text)
    await update.message.reply_text("Сколько метров кабель-канала?")
    return KABELKANAL

async def get_kanal(update, context):
    context.user_data['kanal'] = int(update.message.text)
    reply_keyboard = [["Да", "Нет"]]
    await update.message.reply_text(
        "Нужна установка и настройка видеорегистратора?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return DVR

async def get_dvr(update, context):
    context.user_data['dvr'] = update.message.text.lower() == "да"
    reply_keyboard = [["Да", "Нет"]]
    await update.message.reply_text(
        "Нужна настройка роутера?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ROUTER

async def get_router(update, context):
    context.user_data['router'] = update.message.text.lower() == "да"
    c = context.user_data
    total = (
        c['cameras'] * 1800 +
        c['cable'] * 50 +
        c['gofra'] * 80 +
        c['kanal'] * 50 +
        (2500 if c['dvr'] else 0) +
        (1000 if c['router'] else 0)
    )
    reply_keyboard = [["Начать заново"]]
    await update.message.reply_text(
        f"""Расчёт:
Камер: {c['cameras']} × 1800 = {c['cameras'] * 1800}₽
Кабеля: {c['cable']} м × 50 = {c['cable'] * 50}₽
Гофры: {c['gofra']} м × 80 = {c['gofra'] * 80}₽
Кабель-канала: {c['kanal']} м × 50 = {c['kanal'] * 50}₽
Видеорегистратор: {'2500₽' if c['dvr'] else 'не требуется'}
Настройка роутера: {'1000₽' if c['router'] else 'не требуется'}

ИТОГО: {total}₽
Нажмите /start или кнопку ниже, чтобы начать заново.""",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ConversationHandler.END

# Комплект
async def get_kit_cameras(update, context):
    context.user_data['kit_cameras'] = int(update.message.text)
    reply_keyboard = [["Да", "Нет"]]
    await update.message.reply_text("Нужен видеорегистратор?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return KIT_DVR

async def get_kit_dvr(update, context):
    context.user_data['kit_dvr'] = update.message.text.lower() == "да"
    reply_keyboard = [["Да", "Нет"]]
    await update.message.reply_text("Нужен жёсткий диск?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return KIT_HDD

async def get_kit_hdd(update, context):
    context.user_data['kit_hdd'] = update.message.text.lower() == "да"
    c = context.user_data
    total = (
        c['kit_cameras'] * 2500 +
        (5000 if c['kit_dvr'] else 0) +
        (4000 if c['kit_hdd'] else 0)
    )
    reply_keyboard = [["Начать заново"]]
    await update.message.reply_text(
        f"""Комплект:
Камеры: {c['kit_cameras']} × 2500 = {c['kit_cameras'] * 2500}₽
Видеорегистратор: {'5000₽' if c['kit_dvr'] else 'не требуется'}
Жёсткий диск: {'4000₽' if c['kit_hdd'] else 'не требуется'}

ИТОГО: {total}₽
Нажмите /start или кнопку ниже, чтобы начать заново.""",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ConversationHandler.END

async def cancel(update, context):
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END

app = Application.builder().token(TOKEN).build()

conv = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        CHOOSE_SECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_section)],
        MONTAJ_CAMERAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_cameras)],
        CABLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_cable)],
        GOFRA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_gofra)],
        KABELKANAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_kanal)],
        DVR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_dvr)],
        ROUTER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_router)],
        KIT_CAMERAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_kit_cameras)],
        KIT_DVR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_kit_dvr)],
        KIT_HDD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_kit_hdd)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)

app.add_handler(conv)
app.run_polling()
