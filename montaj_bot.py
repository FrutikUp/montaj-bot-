from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

(CAMERAS, CABLE, GOFRA, KABELKANAL, DVR, ROUTER, RESTART) = range(7)

async def start(update, context):
    await update.message.reply_text("Сколько камер нужно установить?", reply_markup=ReplyKeyboardRemove())
    return CAMERAS

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

    reply_text = f"""Расчёт:
Камер: {c['cameras']} × 1800 = {c['cameras'] * 1800}₽
Кабеля: {c['cable']} м × 50 = {c['cable'] * 50}₽
Гофры: {c['gofra']} м × 80 = {c['gofra'] * 80}₽
Кабель-канала: {c['kanal']} м × 50 = {c['kanal'] * 50}₽
Видеорегистратор: {'2500₽' if c['dvr'] else 'не требуется'}
Настройка роутера: {'1000₽' if c['router'] else 'не требуется'}

ИТОГО: {total}₽"""

    reply_keyboard = [["Начать заново", "Выход"]]
    await update.message.reply_text(reply_text)
    await update.message.reply_text(
        "Что хотите сделать дальше?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return RESTART

async def restart_or_exit(update, context):
    if update.message.text == "Начать заново":
        return await start(update, context)
    else:
        await update.message.reply_text("Спасибо! Если нужно будет снова — напишите /start.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

async def cancel(update, context):
    await update.message.reply_text("Операция отменена.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

app = Application.builder().token("ТВОЙ_ТОКЕН").build()

conv = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        CAMERAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_cameras)],
        CABLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_cable)],
        GOFRA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_gofra)],
        KABELKANAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_kanal)],
        DVR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_dvr)],
        ROUTER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_router)],
        RESTART: [MessageHandler(filters.TEXT & ~filters.COMMAND, restart_or_exit)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)

app.add_handler(conv)
app.run_polling()
