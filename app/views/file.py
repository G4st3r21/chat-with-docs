import os
from aiohttp import ClientSession

from fastapi import APIRouter, UploadFile, File
from utils import *

file_router = APIRouter()
token = "5986084810:AAG14PDKkXEjZ64B3utHff7heO4KHL5kaZA"


async def send_request_and_receive_file(file_path: str):
    telegram_file_url = f"https://api.telegram.org/file/bot{token}/{file_path}"

    async with ClientSession() as session:
        async with session.get(telegram_file_url) as response:
            if response.status != 200:
                return None

            file_name = os.path.basename(file_path)
            with open(f"files/{file_name}", "wb") as file:
                file.write(await response.read())

            return file_name


@file_router.get("/files/{file_path}")
async def get_text_from_file(file_path: str):
    file_name = await send_request_and_receive_file(f"documents/{file_path}")

    file_extension = os.path.splitext(file_name)[1]

    if file_extension.lower() not in [".pdf", ".txt", ".jpeg"]:
        return {"error": "Файл должен быть формата PDF или TXT или JPEG"}

    processed_text = await extract_text_from_file(file_name)
    openai_answer = await send_text_to_neural_network(file_name, file_extension, processed_text)

    return {"text": openai_answer}
