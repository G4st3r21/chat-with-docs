import openai
import asyncio

api_key = "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"


async def send_text_to_neural_network(file_name, file_format, file_text):
    openai.api_key = api_key

    prompt = f"Анализ текста из файла {file_name} формата {file_format}:\n\n{file_text}"

    response = await asyncio.create_task(openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=prompt,
        max_tokens=100,
        temperature=0.7,
        n=1,
        stop=None
    ))

    # Получаем ответ от нейросети
    generated_text = response.choices[0].text.strip()

    return generated_text
