from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

TOKEN = "ТВОЙ_ТОКЕН"

# Состояния
MENU, CAMERAS, CABLE, GOFRA, KABELKANAL, DVR, ROUTER = range(7)

async def start(update, context):
    keyboard = [[KeyboardButton("Монтажные работы")], [KeyboardButton("Готовый комплект камер")]]
    await update.message.reply_text("Привет! Чем могу помочь?", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return MENU

async def menu(update, context):
    text = update.message.text
    if text == "Монтажные работы":
        await update.message.reply_text("Сколько камер нужно установить?", reply_markup=ReplyKeyboardRemove())
        return CAMERAS
    elif text == "Готовый комплект камер":
        await update.message.reply_text("Готовые комплекты:
1 камера — 5000₽
2 камеры — 9000₽
4 камеры — 17000₽

Нажмите /start для возврата в меню.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        await update.message.reply_text("Пожалуйста, выбери вариант с кнопки.")
        return MENU

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
    await update.message.reply_text("Нужна установка видеорегистратора?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    return DVR

async def get_dvr(update, context):
    context.user_data['dvr'] = update.message.text.lower() == "да"
    reply_keyboard = [["Да", "Нет"]]
    await update.message.reply_text("Нужна настройка роутера?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
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

    await update.message.reply_text(
        f"""Расчёт:
Камер: {c['cameras']} × 1800 = {c['cameras'] * 1800}₽
Кабеля: {c['cable']} м × 50 = {c['cable'] * 50}₽
Гофры: {c['gofra']} м × 80 = {c['gofra'] * 80}₽
Кабель-канала: {c['kanal']} м × 50 = {c['kanal'] * 50}₽
Видеорегистратор: {'2500₽' if c['dvr'] else 'не требуется'}
Настройка роутера: {'1000₽' if c['router'] else 'не требуется'}

ИТОГО: {total}₽""",
        reply_markup=ReplyKeyboardMarkup([["Начать заново"]], resize_keyboard=True)
    )
    return MENU

async def cancel(update, context):
    await update.message.reply_text("Операция отменена.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

app = Application.builder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu)],
        CAMERAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_cameras)],
        CABLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_cable)],
        GOFRA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_gofra)],
        KABELKANAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_kanal)],
        DVR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_dvr)],
        ROUTER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_router)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(conv_handler)
app.run_polling()
