import asyncio
import logging
import sys

from aiohttp import ClientSession
from aiogram import Bot, types, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)
bot = Bot("5986084810:AAG14PDKkXEjZ64B3utHff7heO4KHL5kaZA", parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())


@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.reply("Привет! Отправь мне файл для анализа.")


@dp.message(F.photo | F.document)
async def file_handler(message: types.Message):
    file_id = message.document.file_id if message.document else message.photo[-1].file_id
    file_path = await bot.get_file(file_id)
    analysis_result = await send_file_to_server(file_path)
    await message.reply(analysis_result)


async def send_file_to_server(file):
    url = "http://127.0.0.1:8000/files/"
    async with ClientSession() as session:
        async with session.get(url+file.file_path.split("/")[-1]) as response:
            if response.status != 200:
                return "Ошибка при получении файла"

            return response.text


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(dp.start_polling(bot))
