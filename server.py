import os
import secrets

from fastapi.staticfiles import StaticFiles
from config import settings
from typing import Union
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import FileResponse, HTMLResponse
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
# app.mount("/app", StaticFiles(directory="./public", html=True, check_dir=True))
# @app.get("/{path:path}")
# def serve_file_or_index(path: str,req: Request, call_next):
#     file_path = f"public/{path}"
#     if os.path.isfile(file_path):
#         return FileResponse(file_path)
#     else:
#         index_file_path = "public/index.html"
#         if os.path.isfile(index_file_path):
#             return HTMLResponse(open(index_file_path).read())
#         else:
#             return HTMLResponse("Index file not found", status_code=404)

app.include_router(router=apiRouter, prefix="/api")
