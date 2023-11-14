from fastapi import FastAPI
from views import file_router

app = FastAPI()

app.include_router(file_router)

