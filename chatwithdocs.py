from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
import telebot
import os
from pymongo import MongoClient
import PyPDF2
import io
import pytesseract
from PIL import Image
import openai

api_key = "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"
openai.api_key = api_key


def generate_response(user_message):
    prompt = f"User: {user_message}\nChatGPT:"

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.7
    )

    chatbot_response = response.choices[0].text

    return chatbot_response


# load_dotenv() TODO: DOTENV
TELEGRAM_BOT_TOKEN = os.getenv('AAFdhF_z8oHpuvyOaHS6I3lgXeo8nsVXB8g')
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

MONGODB_URI = os.getenv('MONGODB_URI')

client = MongoClient(MONGODB_URI)
db = client['your_database_name']
analytics_collection = db['analytics']

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


@bot.message_handler(content_types=['text'])
def handle_message(message):
    user_id = message.from_user.id
    user_input = message.text

    chatbot_response = generate_response(user_input)

    bot.send_message(user_id, chatbot_response)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Welcome to the PDF Chatbot! Upload a PDF,TXT document or photo and ask questions."
    )


@bot.message_handler(content_types=['document'])
def handle_document(message):
    document_id = message.document.file_id

    file_info = bot.get_file(document_id)
    downloaded_file = bot.download_file(file_info.file_path)

    text = extract_text_from_pdf(downloaded_file)

    log_analytics(message.from_user.id, text)


text_splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len
)

embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_texts(texts=[], embedding=embeddings)

llm = ChatOpenAI()
memory = ConversationBufferMemory(
    memory_key='chat_history',
    return_messages=True
)
conversation_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    memory=memory
)


@bot.message_handler(content_types=['text', 'document', 'photo'])
def handle_message(message):
    user_id = message.from_user.id
    user_input = message.text

    if 'chat_history' in st.session_state:
        chat_history = st.session_state['chat_history']
    else:
        chat_history = []

    if user_input:
        chat_history.append({'role': 'user', 'content': user_input})
        response = conversation_chain({'question': user_input, 'chat_history': chat_history})

        if response:
            chat_history.append({'role': 'bot', 'content': response['chat_history'][-1].content})

    if message.content_type in ['document', 'text']:
        document_text = extract_text_from_document(message)
        chat_history.append({'role': 'user', 'content': document_text})
        response = conversation_chain({'question': document_text, 'chat_history': chat_history})

        if response:
            chat_history.append({'role': 'bot', 'content': response['chat_history'][-1].content})

    if message.content_type == 'photo':
        image_text = extract_text_from_image(message)
        chat_history.append({'role': 'user', 'content': image_text})
        response = conversation_chain({'question': image_text, 'chat_history': chat_history})

        if response:
            chat_history.append({'role': 'bot', 'content': response['chat_history'][-1].content})

    for message in chat_history:
        bot.send_message(user_id, message['content'])

    st.session_state['chat_history'] = chat_history


def extract_text_from_document(message):
    if message.content_type == 'document':
        if message.document.file_name.endswith('.pdf'):
            pdf_file = bot.get_file(message.document.file_id)
            pdf_content = bot.download_file(pdf_file.file_path)
            text = extract_text_from_pdf(pdf_content)
        else:
            txt_file = bot.get_file(message.document.file_id)
            txt_content = bot.download_file(txt_file.file_path)
            text = txt_content.decode('utf-8')

    return text


def extract_text_from_image(image_file):
    try:
        image = Image.open(io.BytesIO(image_file))
        image_text = pytesseract.image_to_string(image, lang='eng')
        return image_text
    except Exception as e:
        print("Error extracting text from image:", str(e))
        return None


if message.content_type == 'photo':
    image_text = extract_text_from_image(image_file)
    if image_text:
        chat_history.append({'role': 'user', 'content': image_text})
    else:
        chat_history.append({'role': 'user', 'content': 'Could not extract text from the image.'})


def extract_text_from_pdf(pdf_content):
    text = ""
    try:
        pdf_file = PyPDF2.PdfFileReader(io.BytesIO(pdf_content))

        for page_number in range(pdf_file.getNumPages()):
            page = pdf_file.getPage(page_number)
            text += page.extractText()
    except Exception as e:
        print("Error extracting text from PDF:", str(e))

    return text


@bot.message_handler(commands=['payment'])
def handle_payment(message):
    user_id = message.from_user.id
    payment_link = create_payment_link(user_id)
    bot.send_message(user_id, f"Click the link to make a payment: {payment_link}")


def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        pdf_reader = PyPDF2.PdfFileReader(pdf_file)

        for page_number in range(pdf_reader.getNumPages()):
            page = pdf_reader.getPage(page_number)
            text += page.extractText()
    except Exception as e:
        print("Error extracting text from PDF:", str(e))

    return text


def log_analytics(user_id, interaction_type, content):
    try:
        analytics_data = {
            "user_id": user_id,
            "interaction_type": interaction_type,
            "content": content
        }
        analytics_collection.insert_one(analytics_data)
    except Exception as e:
        print("Error logging analytics data:", str(e))


def log_analytics_auto(user_id, interaction_type, content):
    user_id = message.from_user.id
    content = message.text

    content_sources = {
        "user_input": content,
        "document": extracted_text,
        "image": extracted_image_text
    }

    try:
        analytics_data = {
            "user_id": user_id,
            "interaction_type": interaction_type,
            "content": content_sources.get(interaction_type, "Unknown")
        }
        analytics_collection.insert_one(analytics_data)
    except Exception as e:
        print("Error logging analytics data:", str(e))


if __name__ == '__main__':
    bot.polling()
