from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, FSInputFile, CallbackQuery,InlineKeyboardButton
import re
from aiogram.types import Message
import asyncio
import logging
from aiogram.fsm.context import FSMContext

# [[types.KeyboardButton(text="Да")]]

BOT_TOKEN = '6913855150:AAHw0WTQFoAisSbv3ZnTIyK87BU8k7csq5Y'

confirm = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='ДА!', callback_data="yes")]
])

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
c_step = {}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

async def main():
    await dp.start_polling(bot)


# Обработчик команды /start
@dp.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    user_name = message.from_user.username
    await message.answer(f"{user_name}, Добро пожаловать в компанию DamnIT")
    await ask_full_name(message)


# Функция для запроса ФИО
async def ask_full_name(message: Message):
    await message.reply("Напишите свое ФИО (без цифр):")
    c_step[message.from_user.id] = "full_name"

# Функция для запроса номера телефона
async def ask_phone_number(message:Message):
    await message.reply("Укажите Ваш номер телефона (в формате 7 999 999 99 99):")
    c_step[message.from_user.id] = "phone_number"

# Функция для запроса комментария
async def ask_comment(message: Message):
    await message.reply("Напишите любой комментарий:")
    c_step[message.from_user.id] = "comment"

async def send_thanks(message: Message):
    await message.answer("Спасибо за успешную регистрацию")
    doc = FSInputFile('img.png')
    await bot.send_document(chat_id=message.from_user.id, document=doc)

@dp.message()
async def handle_request(message: Message):
    user_id = message.from_user.id
    if c_step.get(user_id) == "full_name":
        if not any(char.isdigit() for char in message.text):
            await ask_phone_number(message)
        else:
            await message.reply("ФИО не должно содержать цифры. Попробуйте еще раз.")
    elif c_step.get(user_id) == "phone_number":
        if re.match(r'^7 \d{3} \d{3} \d{2} \d{2}$', message.text):
            await ask_comment(message)
        else:
            await message.reply("Неправильный формат номера. Попробуйте еще раз.")
    elif c_step.get(user_id) == "comment":
        await message.reply("Хорошо")
        await message.answer("Последний шаг! Ознакомьтесь с вводными положениями.")
        doc = FSInputFile('test.pdf')
        await bot.send_document(chat_id=message.from_user.id, document=doc)
        await message.answer("Ознакомился?", reply_markup=confirm)

@dp.callback_query(F.data == "yes")
async def answer_yes(callback: CallbackQuery, state: FSMContext):
    img = FSInputFile('img.png')
    await bot.send_photo(chat_id=callback.from_user.id, photo=img, caption="Спасибо за успешную регистрацию")
    data = await state.get_data()
    await bot.send_message(chat_id="647876155", text=f'Новая заявка от {callback.from_user.id}:\nФИО: {data['name']}\nНомер: {data["number"]}\nКомментарий: {data["comment"]}')
    await state.clear()

if __name__ == '__main__':
    asyncio.run(main())

