from typing import Annotated
from fastapi import HTTPException, Request, Response, Header
import jwt
from config import settings
from jwt import PyJWTError

# Secret key to decode JWT token
SECRET_KEY = settings.get("SECRET")
ALGORITHM = "HS256"

async def authenticate(authorization: Annotated[str, Header()],request: Request):
    if not authorization:
        raise HTTPException(status_code=400, detail="Authorization token not provided")

    try:
        payload = jwt.decode(authorization, SECRET_KEY, algorithms=[ALGORITHM])
        request.session.setdefault("user", payload)
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    