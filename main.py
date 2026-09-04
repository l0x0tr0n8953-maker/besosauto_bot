import logging

import asyncio

import os

from aiogram import Bot, Dispatcher, types

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from aiogram.utils import executor

API_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 413820160

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)

dp = Dispatcher(bot)

users_data = {}

# 📱 телефон

phone_kb = ReplyKeyboardMarkup(resize_keyboard=True)

phone_kb.add(KeyboardButton("📱 Отправить номер", request_contact=True))

# 🚗 ВСЕ МАРКИ

BRANDS = [

    "Toyota", "Kia", "Hyundai", "Chevrolet", "Ford",

    "Volkswagen", "Nissan", "Honda", "Subaru", "Mercedes",

    "BMW", "Citroen", "Suzuki", "Jeep", "Lexus",

    "Mazda", "Peugeot", "Skoda", "Volvo", "Tesla", 

    "Audi",

    "✍️ Свой вариант"

]

# 🚘 ВСЕ МОДЕЛИ

MODELS = {

    "Toyota": ["Camry", "RAV4", "Corolla", "Prius", "Supra", "Land Cruiser", "Yaris"],

    "Kia": ["Forte", "Sportage", "Niro", "Optima", "K5", "K4", "Sorento", "Seltos", "Soul", "Carnival"],

    "Hyundai": ["Elantra", "Tucson", "Kona", "Sonata", "Accent", "Santa Cruz"],

    "Chevrolet": ["Malibu", "Blazer", "Trailblazer", "Cruze", "Silverado", "Trax"],

    "Ford": ["Fusion", "Bronco", "Focus", "Edge", "Mustang"],

    "Volkswagen": ["Jetta", "Passat", "Atlas", "Tiguan", "Golf", "Touareg", "Taos", "Arteon"],

    "Nissan": ["Kicks", "Juke", "Note", "Tiida"],

    "Honda": ["Accord", "Civic", "CR-V", "HR-V", "Freed"],

    "Subaru": ["Forester", "Outback", "XV", "Legacy"],

    "Mercedes": ["C300", "E350", "GLE350", "GLS300", "CLA250"],

    "BMW": ["X5", "X3", "X6", "X7", "X1", "330", "530", "428"],

    "Citroen": ["C3", "C4", "C5"],

    "Suzuki": ["SX4", "Swift", "Vitara", "Grand Vitara", "Jimny"],

    "Jeep": ["Cherokee", "Wrangler", "Grand Cherokee"],

    "Lexus": ["RX350", "GX460", "NX350", "NX300", "RX450", "NX200"],

    "Mazda": ["CX-5", "CX-30", "Mazda 3", "CX-50", "Mazda 6", "CX-90"],

    "Peugeot": ["3008", "308", "307", "406", "508", "5008", "2008", "206"],

    "Skoda": ["Octavia", "Superb", "Rapid", "Fabia", "Kodiaq", "Karoq", "Yeti"],

    "Volvo": ["XC90", "XC60", "XC40", "S60", "S80", "S90", "V40"],

    "Tesla": ["Model 3", "Model Y", "Model S", "Model X", "Cybertruck"],
    
    "Audi": ["Q3", "Q5", "Q7", "Q8", "A3", "A4", "A5", "A6", "A7"]

}

# 🔘 КНОПКА МАРОК

def get_brand_kb():

    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    for i in range(0, len(BRANDS), 2):

        kb.add(*BRANDS[i:i+2])

    return kb

# 🔘 КНОПКА МОДЕЛЕЙ

def get_model_kb(brand):

    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    if brand in MODELS:

        models = MODELS[brand]

        for i in range(0, len(models), 2):

            kb.add(*models[i:i+2])

    kb.add("✍️ Свой вариант")

    return kb

# 🚀 START

@dp.message_handler(commands=['start'])

async def start(message: types.Message):

    user_id = message.from_user.id

    args = message.get_args()

    users_data[user_id] = {

        "step": "brand",

        "source": args if args else "не указан",

        "notified_10": False,

        "notified_60": False

    }

    asyncio.create_task(follow_up(user_id, 600, "notified_10"))

    asyncio.create_task(follow_up(user_id, 3600, "notified_60"))

    if args == "catalog":

        await message.answer("🚘 Выберите марку:", reply_markup=get_brand_kb())

        return

    if args:

        await message.answer(

            f"👋 Вы перешли по объявлению ({args})\n\nВыберите марку:",

            reply_markup=get_brand_kb()

        )

    else:

        await message.answer("🚗 Выберите марку:", reply_markup=get_brand_kb())

# 💬 ОБРАБОТКА

@dp.message_handler()

async def process(message: types.Message):

    user_id = message.from_user.id

    if user_id not in users_data:

        return

    step = users_data[user_id]["step"]

    text = message.text

    # МАРКА

    if step == "brand":

        users_data[user_id]["brand"] = text

        users_data[user_id]["step"] = "model"

        await message.answer("🚘 Выберите модель:", reply_markup=get_model_kb(text))

    # МОДЕЛЬ

    elif step == "model":

        users_data[user_id]["model"] = text

        users_data[user_id]["step"] = "budget"

        kb = ReplyKeyboardMarkup(resize_keyboard=True)

        kb.add("💰 до 2 млн", "💰 2–3 млн")

        kb.add("💰 3+ млн")

        await message.answer(

            f"🚗 Вы выбрали: {users_data[user_id]['brand']} {text}\n\n💰 Выберите бюджет:",

            reply_markup=kb

        )

    # БЮДЖЕТ

    elif step == "budget":

        users_data[user_id]["budget"] = text

        users_data[user_id]["step"] = "phone"

        await message.answer("📱 Отправьте номер:", reply_markup=phone_kb)

# 📞 ТЕЛЕФОН

@dp.message_handler(content_types=['contact'])

async def get_phone(message: types.Message):

    user_id = message.from_user.id

    if user_id not in users_data:

        return

    phone = message.contact.phone_number

    data = users_data[user_id]

    text = (

        f"🚗 Новая заявка!\n\n"

        f"👤 @{message.from_user.username}\n"

        f"🆔 {user_id}\n\n"

        f"🚘 Марка: {data.get('brand')}\n"

        f"🚘 Модель: {data.get('model')}\n"

        f"💰 Бюджет: {data.get('budget')}\n"

        f"📱 Телефон: {phone}\n"

        f"🔗 Источник: {data.get('source')}"

    )

    await bot.send_message(ADMIN_ID, text)

    await message.answer("✅ Заявка отправлена!")

    users_data.pop(user_id, None)

# ⏰ АНТИСПАМ

async def follow_up(user_id, delay, flag):

    await asyncio.sleep(delay)

    if user_id in users_data:

        if not users_data[user_id].get(flag):

            users_data[user_id][flag] = True

            if "phone" not in users_data[user_id]:

                await bot.send_message(

                    user_id,

                    "👋 Вы не оставили номер. Помогу подобрать авто 🚗"

                )

if __name__ == "__main__":

    executor.start_polling(dp, skip_updates=True)
