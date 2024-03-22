import secrets
from config import settings
from typing import Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.models.user import User
from db import Session, engine

from starlette.middleware.sessions import SessionMiddleware

from routes import apiRouter

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=settings.get("SECRET"))

app.include_router(router=apiRouter, prefix="/api")



