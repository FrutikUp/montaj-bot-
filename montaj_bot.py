
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode

TOKEN = "8157090611:AAF-tltFHeHE9r9LuCBMXS4UqsIt09SO7VE"

# Этапы разговора
(CAMERAS, CABLE, GOFRA, KABELKANAL, DVR, ROUTER) = range(6)

def make_keyboard(options):
    return InlineKeyboardMarkup.from_column([InlineKeyboardButton(str(opt), callback_data=str(opt)) for opt in options])

async def start(update: Update, context):
    await update.message.reply_text("Сколько камер нужно установить?", reply_markup=make_keyboard(range(1, 9)))
    return CAMERAS

async def get_cameras(update: Update, context):
    context.user_data['cameras'] = int(update.callback_query.data)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Сколько метров кабеля?", reply_markup=make_keyboard(range(10, 110, 10)))
    return CABLE

async def get_cable(update: Update, context):
    context.user_data['cable'] = int(update.callback_query.data)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Сколько метров гофры?", reply_markup=make_keyboard(range(10, 110, 10)))
    return GOFRA

async def get_gofra(update: Update, context):
    context.user_data['gofra'] = int(update.callback_query.data)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Сколько метров кабель-канала?", reply_markup=make_keyboard(range(10, 110, 10)))
    return KABELKANAL

async def get_kanal(update: Update, context):
    context.user_data['kanal'] = int(update.callback_query.data)
    await update.callback_query.answer()
    keyboard = InlineKeyboardMarkup.from_row([
        InlineKeyboardButton("Да", callback_data="да"),
        InlineKeyboardButton("Нет", callback_data="нет")
    ])
    await update.callback_query.edit_message_text("Нужна установка видеорегистратора?", reply_markup=keyboard)
    return DVR

async def get_dvr(update: Update, context):
    context.user_data['dvr'] = update.callback_query.data == "да"
    await update.callback_query.answer()
    keyboard = InlineKeyboardMarkup.from_row([
        InlineKeyboardButton("Да", callback_data="да"),
        InlineKeyboardButton("Нет", callback_data="нет")
    ])
    await update.callback_query.edit_message_text("Нужна настройка роутера?", reply_markup=keyboard)
    return ROUTER

async def get_router(update: Update, context):
    context.user_data['router'] = update.callback_query.data == "да"
    await update.callback_query.answer()

    c = context.user_data
    total = (
        c['cameras'] * 1800 +
        c['cable'] * 50 +
        c['gofra'] * 80 +
        c['kanal'] * 50 +
        (2500 if c['dvr'] else 0) +
        (1000 if c['router'] else 0)
    )
    text = f"""<b>Расчёт:</b>
Камер: {c['cameras']} × 1800 = {c['cameras'] * 1800}₽
Кабеля: {c['cable']} м × 50 = {c['cable'] * 50}₽
Гофры: {c['gofra']} м × 80 = {c['gofra'] * 80}₽
Кабель-канала: {c['kanal']} м × 50 = {c['kanal'] * 50}₽
Видеорегистратор: {'2500₽' if c['dvr'] else 'не требуется'}
Настройка роутера: {'1000₽' if c['router'] else 'не требуется'}

<b>ИТОГО: {total}₽</b>
Нажмите /start, чтобы начать заново."""
    await update.callback_query.edit_message_text(text, parse_mode=ParseMode.HTML)
    return ConversationHandler.END

app = Application.builder().token(TOKEN).build()

conv = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        CAMERAS: [CallbackQueryHandler(get_cameras)],
        CABLE: [CallbackQueryHandler(get_cable)],
        GOFRA: [CallbackQueryHandler(get_gofra)],
        KABELKANAL: [CallbackQueryHandler(get_kanal)],
        DVR: [CallbackQueryHandler(get_dvr)],
        ROUTER: [CallbackQueryHandler(get_router)],
    },
    fallbacks=[]
)

app.add_handler(conv)
app.run_polling()
