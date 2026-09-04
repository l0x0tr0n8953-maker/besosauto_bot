import logging

import os

import asyncio

from aiogram import Bot, Dispatcher, types

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.utils import executor

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher(bot)

users_data = {}

# 📱 КНОПКА НОМЕРА

phone_kb = ReplyKeyboardMarkup(resize_keyboard=True)

phone_kb.add(KeyboardButton("📱 Отправить номер", request_contact=True))

# 💰 КНОПКИ БЮДЖЕТА

budget_kb = InlineKeyboardMarkup(row_width=2)

budget_kb.add(

    InlineKeyboardButton("💰 до 2 млн", callback_data="budget_2"),

    InlineKeyboardButton("💰 2–3 млн", callback_data="budget_3"),

    InlineKeyboardButton("💰 3+ млн", callback_data="budget_4"),

)

# 📞 КНОПКА ПОЗВОНИТЬ

def call_kb(phone):

    kb = InlineKeyboardMarkup()

    kb.add(InlineKeyboardButton("📞 Позвонить", url=f"tel:{phone}"))

    return kb

# 🚀 СТАРТ

@dp.message_handler(commands=['start'])

async def start(message: types.Message):

    user_id = message.from_user.id

    users_data[user_id] = {"step": "brand"}

    source = message.get_args()

    if source:

        nice_source = source.replace("_", " ").title()

        users_data[user_id]["source"] = nice_source

        parts = source.split("_")

        # авто-подстановка

        if len(parts) >= 2:

            users_data[user_id]["brand"] = parts[0].capitalize()

            users_data[user_id]["model"] = parts[1].capitalize()

            users_data[user_id]["step"] = "budget"

            await message.answer(

                f"🚗 Вы выбрали: {parts[0].capitalize()} {parts[1].capitalize()}"

            )

            await message.answer("💰 Выберите бюджет:", reply_markup=budget_kb)

            return

    users_data[user_id]["source"] = "Не указано"

    await message.answer("🚗 Какая марка авто интересует?")

# 🔥 ОБРАБОТКА ШАГОВ

@dp.message_handler()

async def process(message: types.Message):

    user_id = message.from_user.id

    if user_id not in users_data:

        return

    step = users_data[user_id].get("step")

    # Марка

    if step == "brand":

        users_data[user_id]["brand"] = message.text

        users_data[user_id]["step"] = "model"

        await message.answer("🚘 Модель?")

    # Модель

    elif step == "model":

        users_data[user_id]["model"] = message.text

        users_data[user_id]["step"] = "budget"

        await message.answer("💰 Выберите бюджет:", reply_markup=budget_kb)

    # Если бюджет текстом

    elif step == "budget":

        users_data[user_id]["budget"] = message.text

        users_data[user_id]["step"] = "phone"

        await message.answer("📱 Отправьте номер", reply_markup=phone_kb)

# 💰 ОБРАБОТКА КНОПОК БЮДЖЕТА

@dp.callback_query_handler(lambda c: c.data.startswith("budget"))

async def process_budget(callback_query: types.CallbackQuery):

    user_id = callback_query.from_user.id

    mapping = {

        "budget_2": "до 2 млн",

        "budget_3": "2–3 млн",

        "budget_4": "3+ млн",

    }

    users_data[user_id]["budget"] = mapping.get(callback_query.data)

    users_data[user_id]["step"] = "phone"

    await bot.send_message(user_id, "📱 Отправьте номер телефона", reply_markup=phone_kb)

# 📱 ПОЛУЧЕНИЕ ТЕЛЕФОНА

@dp.message_handler(content_types=['contact'])

async def get_phone(message: types.Message):

    user = message.from_user

    user_id = user.id

    data = users_data.get(user_id, {})

    phone = message.contact.phone_number

    text = f"""

🚗 Новая заявка!

📍 Источник: {data.get("source")}

👤 @{user.username}

🆔 {user.id}

🚗 Марка: {data.get("brand")}

🚘 Модель: {data.get("model")}

💰 Бюджет: {data.get("budget")}

📱 Телефон: {phone}

"""

    await bot.send_message(ADMIN_ID, text)

    await bot.send_message(ADMIN_ID, "Связаться:", reply_markup=call_kb(phone))

    await message.answer(

        "✅ Заявка отправлена! Скоро с вами свяжемся.",

        reply_markup=types.ReplyKeyboardRemove()

    )
    users_data.pop(user_id, None)

# ⏱ АВТОДОЖИМ

async def follow_up(user_id):

    await asyncio.sleep(120)

    if user_id in users_data:

        await bot.send_message(

            user_id,

            "👋 Вы не оставили номер.\nМогу подобрать авто под ваш бюджет 🚗"

        )

# fallback (не мешает логике)

@dp.message_handler(lambda message: message.from_user.id not in users_data)

async def fallback(message: types.Message):

    pass

# 🚀 ЗАПУСК

if __name__ == "__main__":

    executor.start_polling(dp, skip_updates=True)
