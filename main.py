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

tasks = {}

# 📱 кнопка телефона

phone_kb = ReplyKeyboardMarkup(resize_keyboard=True)

phone_kb.add(KeyboardButton("📱 Отправить номер", request_contact=True))

# 🚗 БАЗА

cars = {

    "Toyota": ["Camry","RAV4","Corolla","Prius","Supra","Land Cruiser","Yaris"],

    "Kia": ["Forte","Sportage","Niro","Optima","K5","K4","Sorento","Seltos","Soul","Carnival"],

    "Hyundai": ["Elantra","Tucson","Kona","Sonata","Accent","Santa Cruz"],

    "Chevrolet": ["Malibu","Blazer","Trailblazer","Cruze","Silverado","Trax"],

    "Ford": ["Fusion","Bronco","Focus","Edge","Mustang"],

    "Volkswagen": ["Jetta","Passat","Atlas","Tiguan","Golf","Touareg","Taos","Arteon"],

    "Nissan": ["Kicks","Juke","Note","Tiida"],

    "Honda": ["Accord","Civic","CR-V","HR-V","Freed"],

    "Subaru": ["Forester","Outback","XV","Legacy"],

    "Mercedes": ["C300","E350","GLE350","GLS300","CLA250"],

    "BMW": ["X5","X3","X6","X7","X1","330","530","428"],

    "Citroen": ["C3","C4","C5"],

    "Suzuki": ["SX4","Swift","Vitara","Grand Vitara","Jimny"],

    "Jeep": ["Cherokee","Wrangler","Grand Cherokee"],

    "Lexus": ["RX350","GX460","NX350","NX300","RX450","NX200"],

    "Mazda": ["CX-5","CX-30","Mazda 3","CX-50","Mazda 6","CX-90"],

    "Peugeot": ["3008","308","307","406","508","5008","2008","206"],

    "Skoda": ["Octavia","Superb","Rapid","Fabia","Kodiaq","Karoq","Yeti"],

    "Volvo": ["XC90","XC60","XC40","S60","S80","S90","V40"],

    "Tesla": ["Model 3","Model Y","Model S","Model X","Cybertruck"]

}

# 🔘 генерация клавиатуры

def make_kb(items, custom_text):

    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    for i in range(0, len(items), 2):

        kb.row(*items[i:i+2])

    kb.add(custom_text)

    return kb

# 🚀 СТАРТ

@dp.message_handler(commands=['start'])

async def start(message: types.Message):

    user_id = message.from_user.id

    # убираем старые таймеры

    if user_id in tasks:

        for t in tasks[user_id]:

            t.cancel()

    args = message.get_args()

    users_data[user_id] = {

        "step": "brand",

        "source": args if args else "не указан"

    }

    # 🔥 авто-подстановка из кнопки

    if args:

        for brand, models in cars.items():

            for model in models:

                if model.lower().replace(" ", "") in args.lower():

                    users_data[user_id]["brand"] = brand

                    users_data[user_id]["model"] = model

                    users_data[user_id]["step"] = "budget"

                    kb = ReplyKeyboardMarkup(resize_keyboard=True)

                    kb.add("💰 до 2 млн", "💰 2–3 млн")

                    kb.add("💰 3+ млн")

                    await message.answer(

                        f"🚗 Вы выбрали: {brand} {model}\n\n💰 Выберите бюджет:",

                        reply_markup=kb

                    )

                    return

    # обычный старт

    kb = make_kb(list(cars.keys()), "✍️ Другая марка")

    await message.answer("🚗 Выберите марку авто:", reply_markup=kb)

    # напоминание (1 раз)

    t = asyncio.create_task(follow_up(user_id, 600))

    tasks[user_id] = [t]

# 💬 ЛОГИКА

@dp.message_handler()

async def process(message: types.Message):

    user_id = message.from_user.id

    if user_id not in users_data:

        return

    step = users_data[user_id]["step"]

    # 🚗 МАРКА

    if step == "brand":

        if message.text == "✍️ Другая марка":

            users_data[user_id]["step"] = "brand_custom"

            await message.answer("✍️ Напишите марку авто:")

            return

        users_data[user_id]["brand"] = message.text

        users_data[user_id]["step"] = "model"

        models = cars.get(message.text)

        if models:

            kb = make_kb(models, "✍️ Другая модель")

            await message.answer("🚘 Выберите модель:", reply_markup=kb)

        else:

            await message.answer("✍️ Напишите модель:")

    # кастом марка

    elif step == "brand_custom":

        users_data[user_id]["brand"] = message.text

        users_data[user_id]["step"] = "model"

        await message.answer("✍️ Напишите модель:")

    # 🚘 МОДЕЛЬ

    elif step == "model":

        if message.text == "✍️ Другая модель":

            users_data[user_id]["step"] = "model_custom"

            await message.answer("✍️ Напишите модель:")

            return

        users_data[user_id]["model"] = message.text

        users_data[user_id]["step"] = "budget"

        kb = ReplyKeyboardMarkup(resize_keyboard=True)

        kb.add("💰 до 2 млн", "💰 2–3 млн")

        kb.add("💰 3+ млн")

        await message.answer("💰 Выберите бюджет:", reply_markup=kb)

    # кастом модель

    elif step == "model_custom":

        users_data[user_id]["model"] = message.text

        users_data[user_id]["step"] = "budget"

        kb = ReplyKeyboardMarkup(resize_keyboard=True)

        kb.add("💰 до 2 млн", "💰 2–3 млн")

        kb.add("💰 3+ млн")

        await message.answer("💰 Выберите бюджет:", reply_markup=kb)

    # 💰 бюджет

    elif step == "budget":

        users_data[user_id]["budget"] = message.text

        users_data[user_id]["step"] = "phone"

        await message.answer("📱 Отправьте номер телефона:", reply_markup=phone_kb)

# 📞 ТЕЛЕФОН

@dp.message_handler(content_types=['contact'])

async def get_phone(message: types.Message):

    user_id = message.from_user.id

    if user_id not in users_data:

        return

    data = users_data[user_id]

    phone = message.contact.phone_number

    text = (

        f"🚗 Новая заявка\n\n"

        f"👤 @{message.from_user.username}\n"

        f"🆔 {user_id}\n\n"

        f"Марка: {data.get('brand')}\n"

        f"Модель: {data.get('model')}\n"

        f"Бюджет: {data.get('budget')}\n"

        f"Телефон: {phone}\n"

        f"Источник: {data.get('source')}"

    )

    await bot.send_message(ADMIN_ID, text)

    await message.answer("✅ Заявка отправлена! Мы скоро свяжемся с вами.")

    # стоп таймеров

    if user_id in tasks:

        for t in tasks[user_id]:

            t.cancel()

    users_data.pop(user_id, None)

    tasks.pop(user_id, None)

# ⏰ НАПОМИНАНИЕ

async def follow_up(user_id, delay):

    try:

        await asyncio.sleep(delay)

        if user_id in users_data and "phone" not in users_data[user_id]:

            await bot.send_message(

                user_id,

                "👋 Вы не оставили номер.\nПодберу авто под ваш бюджет 🚗"

            )

    except:

        pass

# ▶️ запуск

if __name__ == "__main__":

    executor.start_polling(dp, skip_updates=True)
