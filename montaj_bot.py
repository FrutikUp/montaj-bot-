from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from telegram import ReplyKeyboardMarkup

# Токен от BotFather
TOKEN = '8157090611:AAF-tltFHeHE9r9LuCBMXS4UqsIt09SO7VE'

# Этапы разговора
(MONTAJ_CAMERAS, MONTAJ_CABLE, MONTAJ_GOFRA, MONTAJ_KABELKANAL, MONTAJ_DVR, MONTAJ_ROUTER,
 KIT_CAMERAS, KIT_CABLE, KIT_GOFRA, KIT_KABELKANAL, KIT_DVR, KIT_ROUTER) = range(12)

# Начало
async def start(update, context):
    reply_keyboard = [["Монтажные работы", "Готовый комплект камер"]]
    await update.message.reply_text(
        "Привет! Чем могу помочь?\nВыбери один из вариантов.",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return MONTAJ_CAMERAS

# Монтажные работы
async def start_montaj(update, context):
    await update.message.reply_text("Сколько камер нужно установить?")
    return MONTAJ_CAMERAS

async def get_montaj_cameras(update, context):
    context.user_data['cameras'] = int(update.message.text)
    await update.message.reply_text("Сколько метров кабеля?")
    return MONTAJ_CABLE

async def get_montaj_cable(update, context):
    context.user_data['cable'] = int(update.message.text)
    await update.message.reply_text("Сколько метров кабеля в гофре?")
    return MONTAJ_GOFRA

async def get_montaj_gofra(update, context):
    context.user_data['gofra'] = int(update.message.text)
    await update.message.reply_text("Сколько метров кабель-канала?")
    return MONTAJ_KABELKANAL

async def get_montaj_kanal(update, context):
    context.user_data['kanal'] = int(update.message.text)
    reply_keyboard = [["Да", "Нет"]]
    await update.message.reply_text(
        "Нужна установка и настройка видеорегистратора?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return MONTAJ_DVR

async def get_montaj_dvr(update, context):
    context.user_data['dvr'] = update.message.text.lower() == "да"
    reply_keyboard = [["Да", "Нет"]]
    await update.message.reply_text(
        "Нужна настройка роутера?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return MONTAJ_ROUTER

async def get_montaj_router(update, context):
    context.user_data['router'] = update.message.text.lower() == "да"

    # Расчёт
    c = context.user_data
    total = (
        c['cameras'] * 1800 +
        c['cable'] * 50 +
        c['gofra'] * 80 +
        c['kanal'] * 50 +
        (2500 if c['dvr'] else 0) +
        (1000 if c['router'] else 0)
    )

    await update.message.reply_text(
        f"""Расчёт:
Камер: {c['cameras']} × 1800 = {c['cameras'] * 1800}₽
Кабеля: {c['cable']} м × 50 = {c['cable'] * 50}₽
Гофры: {c['gofra']} м × 80 = {c['gofra'] * 80}₽
Кабель-канала: {c['kanal']} м × 50 = {c['kanal'] * 50}₽
Видеорегистратор: {'2500₽' if c['dvr'] else 'не требуется'}
Настройка роутера: {'1000₽' if c['router'] else 'не требуется'}

ИТОГО: {total}₽"""
    )
    await update.message.reply_text("Хотите начать заново? Напишите /start.")
    return ConversationHandler.END

# Готовый комплект камер
async def start_kit(update, context):
    await update.message.reply_text("Сколько камер в комплекте?")
    return KIT_CAMERAS

async def get_kit_cameras(update, context):
    context.user_data['cameras'] = int(update.message.text)
    await update.message.reply_text("Сколько метров кабеля?")
    return KIT_CABLE

async def get_kit_cable(update, context):
    context.user_data['cable'] = int(update.message.text)
    await update.message.reply_text("Сколько метров кабеля в гофре?")
    return KIT_GOFRA

async def get_kit_gofra(update, context):
    context.user_data['gofra'] = int(update.message.text)
    await update.message.reply_text("Сколько метров кабель-канала?")
    return KIT_KABELKANAL

async def get_kit_kanal(update, context):
    context.user_data['kanal'] = int(update.message.text)
    reply_keyboard = [["Да", "Нет"]]
    await update.message.reply_text(
        "Нужна установка и настройка видеорегистратора?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return KIT_DVR

async def get_kit_dvr(update, context):
    context.user_data['dvr'] = update.message.text.lower() == "да"
    reply_keyboard = [["Да", "Нет"]]
    await update.message.reply_text(
        "Нужна настройка роутера?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return KIT_ROUTER

async def get_kit_router(update, context):
    context.user_data['router'] = update.message.text.lower() == "да"

    # Расчёт
    c = context.user_data
    total = (
        c['cameras'] * 1600 +
        c['cable'] * 40 +
        c['gofra'] * 70 +
        c['kanal'] * 40 +
        (2300 if c['dvr'] else 0) +
        (900 if c['router'] else 0)
    )

    await update.message.reply_text(
        f"""Расчёт:
Камер: {c['cameras']} × 1600 = {c['cameras'] * 1600}₽
Кабеля: {c['cable']} м × 40 = {c['cable'] * 40}₽
Гофры: {c['gofra']} м × 70 = {c['gofra'] * 70}₽
Кабель-канала: {c['kanal']} м × 40 = {c['kanal'] * 40}₽
Видеорегистратор: {'2300₽' if c['dvr'] else 'не требуется'}
Настройка роутера: {'900₽' if c['router'] else 'не требуется'}

ИТОГО: {total}₽"""
    )
    await update.message.reply_text("Хотите начать заново? Напишите /start.")
    return ConversationHandler.END

# Отмена
async def cancel(update, context):
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END

app = Application.builder().token(TOKEN).build()

conv = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        MONTAJ_CAMERAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, start_montaj)],
        MONTAJ_CABLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_montaj_cables)],
        MONTAJ_GOFRA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_montaj_gofra)],
        MONTAJ_KABELKANAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_montaj_kanal)],
        MONTAJ_DVR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_montaj_dvr)],
        MONTAJ_ROUTER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_montaj_router)],

        KIT_CAMERAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, start_kit)],
        KIT_CABLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_kit_cable)],
        KIT_GOFRA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_kit_gofra)],
        KIT_KABELKANAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_kit_kanal)],
        KIT_DVR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_kit_dvr)],
        KIT_ROUTER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_kit_router)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)

app.add_handler(conv)
app.run_polling()