import os
from aiohttp import ClientSession
from os import getenv

from fastapi import APIRouter, UploadFile, File
from starlette.requests import Request

from utils import *

file_router = APIRouter()


@file_router.post("/files")
async def get_text_from_file(request: Request):
    body = await request.json()
    file_name = await send_request_and_receive_file(body, "documents/{file_path}")
    file_extension = os.path.splitext(file_name)[1]

    if file_extension.lower() not in [".pdf", ".txt", ".jpeg"]:
        return {"error": "Файл должен быть формата PDF или TXT или JPEG"}

    processed_text = await extract_text_from_file(file_name)
    openai_answer = await send_text_to_neural_network(file_name, file_extension, processed_text)

    return {"text": openai_answer}


async def send_request_and_receive_file(body):
    telegram_file_url = f"https://api.telegram.org/file/bot{body['bot_token']}/documents/{body['file_name']}"

    async with ClientSession() as session:
        async with session.get(telegram_file_url) as response:
            if response.status != 200:
                return None

            with open(f"files/{body['file_name']}", "wb") as file:
                file.write(await response.read())

            return body['file_name']
