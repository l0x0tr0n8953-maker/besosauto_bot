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

# 📱 Кнопка отправки номера

phone_kb = ReplyKeyboardMarkup(resize_keyboard=True)

phone_kb.add(KeyboardButton("📲 Отправить номер", request_contact=True))

# 💰 Кнопки бюджета

budget_kb = InlineKeyboardMarkup(row_width=2)

budget_kb.add(

    InlineKeyboardButton("💰 до 2 млн", callback_data="budget_2"),

    InlineKeyboardButton("💰 2–3 млн", callback_data="budget_3"),

    InlineKeyboardButton("💰 3+ млн", callback_data="budget_4"),

)

# 📞 Кнопка связаться

def call_kb(phone):

    kb = InlineKeyboardMarkup()

    kb.add(InlineKeyboardButton("📞 Позвонить сразу", url=f"tel:{phone}"))

    return kb

# 🚀 СТАРТ

@dp.message_handler(commands=['start'])

async def start(message: types.Message):

    users_data[message.from_user.id] = {}

    source = message.get_args()

    if source:

        # делаем красивое название

        nice_source = source.replace("_", " ").title()

        users_data[message.from_user.id]["source"] = nice_source

        # авто-подстановка марки и модели

        parts = source.split("_")

        if len(parts) >= 2:

            users_data[message.from_user.id]["brand"] = parts[0].capitalize()

            users_data[message.from_user.id]["model"] = parts[1].capitalize()

            await message.answer(

                f"🚗 Вы выбрали: {parts[0].capitalize()} {parts[1].capitalize()}"

            )

    else:

        users_data[message.from_user.id]["source"] = "Не указано"

        await message.answer("🚗 Какая марка авто интересует?")

        return

    await message.answer("💰 Выберите бюджет:", reply_markup=budget_kb)

# 💰 ОБРАБОТКА БЮДЖЕТА

@dp.callback_query_handler(lambda c: c.data.startswith("budget"))

async def process_budget(callback_query: types.CallbackQuery):

    user_id = callback_query.from_user.id

    mapping = {

        "budget_2": "до 2 млн",

        "budget_3": "2–3 млн",

        "budget_4": "3+ млн"

    }

    users_data[user_id]["budget"] = mapping.get(callback_query.data)

    await bot.send_message(user_id, "📲 Отправьте номер телефона", reply_markup=phone_kb)

# 📞 ПОЛУЧЕНИЕ ТЕЛЕФОНА

@dp.message_handler(content_types=['contact'])

async def get_phone(message: types.Message):

    user = message.from_user

    data = users_data.get(user.id, {})

    phone = message.contact.phone_number

    text = f"""

🚗 Новая заявка!

📍 Источник: {data.get("source")}

👤 @{user.username}

🆔 {user.id}

Марка: {data.get("brand")}

Модель: {data.get("model")}

Бюджет: {data.get("budget")}

Телефон: {phone}

"""

    await bot.send_message(ADMIN_ID, text)

    await bot.send_message(ADMIN_ID, "Связаться:", reply_markup=call_kb(phone))

    await message.answer(

        "✅ Заявка отправлена! Скоро с вами свяжемся.",

        reply_markup=types.ReplyKeyboardRemove()

    )

    users_data.pop(user.id, None)

# 🔁 АВТОДОЖИМ

async def follow_up(user_id):

    await asyncio.sleep(60)

    if user_id in users_data:

        await bot.send_message(

            user_id,

            "👋 Вы не оставили номер.\nМогу подобрать авто под ваш бюджет 🚗"

        )

@dp.message_handler()

async def fallback(message: types.Message):

    user_id = message.from_user.id

    if user_id in users_data and "budget" not in users_data[user_id]:

        asyncio.create_task(follow_up(user_id))

if __name__ == "__main__":

    executor.start_polling(dp, skip_updates=True)
