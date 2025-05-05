import os
from aiogram import Bot, Dispatcher, types, executor
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

PRICE_LIST = {
    "Камера на кронштейн": 800,
    "Камера в потолок": 600,
    "Протяжка 1м кабеля": 25,
    "Настройка регистратора": 1000
}

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for item in PRICE_LIST.keys():
        keyboard.add(item)
    keyboard.add("Посчитать итог")
    await message.answer("Выберите позиции для расчёта:", reply_markup=keyboard)

user_selection = {}

@dp.message_handler(lambda message: message.text in PRICE_LIST)
async def item_handler(message: types.Message):
    user_id = message.from_user.id
    item = message.text
    user_selection.setdefault(user_id, []).append(item)
    await message.answer(f"Добавлено: {item}")

@dp.message_handler(lambda message: message.text == "Посчитать итог")
async def calculate_total(message: types.Message):
    user_id = message.from_user.id
    items = user_selection.get(user_id, [])
    total = sum(PRICE_LIST[item] for item in items)
    summary = "\n".join(items)
    await message.answer(f"Вы выбрали:\n{summary}\n\nИтого: {total} руб.")

if __name__ == '__main__':
    executor.start_polling(dp)
