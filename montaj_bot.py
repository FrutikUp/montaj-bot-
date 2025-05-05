from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ConversationHandler
)
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes

# Этапы
(CAMERAS, CABLE, GOFRA, KABELKANAL, DVR, ROUTER, MENU, KIT_CAMERAS) = range(8)

TOKEN = "8157090611:AAF-tltFHeHE9r9LuCBMXS4UqsIt09SO7VE"

# Главное меню
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Монтаж камер", "Собрать комплект"]]
    await update.message.reply_text(
        "Привет! Чем могу помочь?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return MENU

# Обработка выбора раздела
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text

    if choice == "Монтаж камер":
        await update.message.reply_text("Сколько камер нужно установить?", reply_markup=ReplyKeyboardRemove())
        return CAMERAS
    elif choice == "Собрать комплект":
        await update.message.reply_text("Сколько камер будет в комплекте?", reply_markup=ReplyKeyboardRemove())
        return KIT_CAMERAS
    else:
        await update.message.reply_text("Выберите действие из меню.")
        return MENU

# Монтаж камер
async def get_cameras(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['cameras'] = int(update.message.text)
    await update.message.reply_text("Сколько метров кабеля?")
    return CABLE

async def get_cable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['cable'] = int(update.message.text)
    await update.message.reply_text("Сколько метров кабеля в гофре?")
    return GOFRA

async def get_gofra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['gofra'] = int(update.message.text)
    await update.message.reply_text("Сколько метров кабель-канала?")
    return KABELKANAL

async def get_kanal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['kanal'] = int(update.message.text)
    reply_keyboard = [["Да", "Нет"]]
    await update.message.reply_text(
        "Нужна установка и настройка видеорегистратора?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return DVR

async def get_dvr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['dvr'] = update.message.text.lower() == "да"
    reply_keyboard = [["Да", "Нет"]]
    await update.message.reply_text(
        "Нужна настройка роутера?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ROUTER

async def get_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

Нажмите 'Начать заново' для нового расчета.""",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return MENU

# Сборка комплекта
async def kit_cameras(update: Update, context: ContextTypes.DEFAULT_TYPE):
    num = int(update.message.text)
    price = num * 3000  # примерная стоимость за камеру
    reply_keyboard = [["Начать заново"]]
    await update.message.reply_text(
        f"""Комплект с {num} камерами:
Камеры: {num} × 3000₽ = {price}₽
Регистратор: 5000₽
Блок питания и разветвители: 2000₽

ИТОГО: {price + 5000 + 2000}₽

Нажмите 'Начать заново' для нового расчета.""",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return MENU

# Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Операция отменена.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

app = Application.builder().token(TOKEN).build()

conv = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu)],
        CAMERAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_cameras)],
        CABLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_cable)],
        GOFRA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_gofra)],
        KABELKANAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_kanal)],
        DVR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_dvr)],
        ROUTER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_router)],
        KIT_CAMERAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, kit_cameras)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)

app.add_handler(conv)
app.run_polling()