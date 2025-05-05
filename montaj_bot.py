import logging
import os
import asyncio
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# Токен от BotFather
TOKEN = '8157090611:AAF-tltFHeHE9r9LuCBMXS4UqsIt09SO7VE'

# Этапы разговора
(CAMERAS, CABLE, GOFRA, KABELKANAL, DVR, ROUTER, MENU, KIT_CAMERAS) = range(8)

# Создание приложения для работы с ботом
application = Application.builder().token(TOKEN).build()

# Хэндлеры для логики работы бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [['Монтажные работы', 'Собрать комплект']]
    await update.message.reply_text(
        "Привет! Чем могу помочь?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return MENU

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Монтажные работы":
        await update.message.reply_text("Сколько камер нужно установить?")
        return CAMERAS
    elif text == "Собрать комплект":
        await update.message.reply_text("Выберите комплект: Камеры, кабель, видеорегистратор и т. д.")
        return KIT_CAMERAS

# Логика для Монтажных работ
async def get_cameras(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['cameras'] = int(update.message.text)
        await update.message.reply_text("Сколько метров кабеля?")
        return CABLE
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.")
        return CAMERAS

async def get_cable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['cable'] = int(update.message.text)
        await update.message.reply_text("Сколько метров кабеля в гофре?")
        return GOFRA
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.")
        return CABLE

async def get_gofra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['gofra'] = int(update.message.text)
        await update.message.reply_text("Сколько метров кабель-канала?")
        return KABELKANAL
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.")
        return GOFRA

async def get_kanal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['kanal'] = int(update.message.text)
        reply_keyboard = [["Да", "Нет"]]
        await update.message.reply_text(
            "Нужна установка и настройка видеорегистратора?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return DVR
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.")
        return KABELKANAL

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

    # Добавление кнопки "Вернуться в начало"
    reply_keyboard = [["Вернуться в начало"]]
    
    await update.message.reply_text(
        f"""Расчёт:
Камер: {c['cameras']} × 1800 = {c['cameras'] * 1800}₽
Кабеля: {c['cable']} м × 50 = {c['cable'] * 50}₽
Гофры: {c['gofra']} м × 80 = {c['gofra'] * 80}₽
Кабель-канала: {c['kanal']} м × 50 = {c['kanal'] * 50}₽
Видеорегистратор: {'2500₽' if c['dvr'] else 'не требуется'}
Настройка роутера: {'1000₽' if c['router'] else 'не требуется'}

ИТОГО: {total}₽""",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return MENU  # Переход в меню

async def kit_cameras(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Вы выбрали собирать комплект камер. Какие именно камеры хотите? Пример: '4 камеры', '6 камер' и т.д.")
    return KIT_CAMERAS

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END

# Создание хэндлеров
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

# Добавляем хэндлер
application.add_handler(conv)

# Функция для запуска бота с использованием webhook
async def main():
    # Запуск вебхука
    await application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        url_path="/webhook",
        webhook_url="https://montaj-bot.onrender.com/webhook"
    )

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # Запуск основного процесса
    asyncio.run(main())
