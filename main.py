import logging
import os

from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 413820160  # твой Telegram ID

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)

dp = Dispatcher(bot)

users_data = {}

# Кнопка отправки телефона

phone_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

phone_kb.add(types.KeyboardButton("📱 Отправить номер", request_contact=True))

# СТАРТ

@dp.message_handler(commands=['start'])

async def start(message: types.Message):

    users_data[message.from_user.id] = {"step": "brand"}

    await message.answer("🚗 Какая марка авто интересует?")

# ОСНОВНАЯ ЛОГИКА

@dp.message_handler()

async def process(message: types.Message):

    user_id = message.from_user.id

    if user_id not in users_data:

        return

    step = users_data[user_id].get("step")

    if step == "brand":

        users_data[user_id]["brand"] = message.text

        users_data[user_id]["step"] = "model"

        await message.answer("🚗 Какая модель?")

    elif step == "model":

        users_data[user_id]["model"] = message.text

        users_data[user_id]["step"] = "budget"

        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

        kb.add("💰 до 2 млн", "💰 2–3 млн")

        kb.add("💰 3+ млн")

        await message.answer("💰 Выберите бюджет:", reply_markup=kb)

    elif step == "budget":

        users_data[user_id]["budget"] = message.text

        users_data[user_id]["step"] = "phone"

        await message.answer(

            "📱 Отправьте номер телефона",

            reply_markup=phone_kb

        )

# ПОЛУЧЕНИЕ ТЕЛЕФОНА

@dp.message_handler(content_types=['contact'])

async def get_phone(message: types.Message):

    user_id = message.from_user.id

    data = users_data.get(user_id, {})

    phone = message.contact.phone_number

    text = f"""

🚗 Новая заявка!

👤 @{message.from_user.username}

🆔 {user_id}

🚘 Марка: {data.get("brand")}

🚘 Модель: {data.get("model")}

💰 Бюджет: {data.get("budget")}

📱 Телефон: {phone}

"""

    # Отправляем админу БЕЗ inline-кнопок

    await bot.send_message(ADMIN_ID, text)

    await message.answer("✅ Заявка отправлена!")

    users_data.pop(user_id, None)

# ЗАПУСК (ЭТО ВАЖНО!)

if __name__ == "__main__":

    executor.start_polling(dp, skip_updates=True)
