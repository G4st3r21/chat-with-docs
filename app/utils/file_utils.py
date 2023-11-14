import asyncio
from io import BytesIO

import aiofiles
import PyPDF2
import pytesseract


async def extract_text_from_file(file_path):
    match file_path.split(".")[-1]:
        case "txt":
            return await extract_text_from_txt(file_path)
        case "pdf":
            return await extract_text_from_pdf(file_path)
        case "jpeg":
            return await extract_text_from_jpeg(file_path)
        case _:
            return None


async def extract_text_from_jpeg(file_path):
    async with aiofiles.open(f"files/{file_path}", "rb") as f:
        image_data = await f.read()

    text = await asyncio.to_thread(
        pytesseract.image_to_string,
        image_data,
        lang='ru'
    )

    return text


async def extract_text_from_txt(file_path):
    async with aiofiles.open(f"files/{file_path}", "r") as opened_file:
        content = await opened_file.read()

    return content


async def extract_text_from_pdf(file_path):
    async with aiofiles.open(f"files/{file_path}", "rb") as opened_file:
        content = await opened_file.read()

    pdf_reader = PyPDF2.PdfReader(BytesIO(content))
    num_pages = len(pdf_reader.pages)
    text = "".join([pdf_reader.pages[page_num].extract_text() for page_num in range(num_pages)])

    return text
