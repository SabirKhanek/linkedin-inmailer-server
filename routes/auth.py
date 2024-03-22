from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from common.exceptions import InvalidCredentialsException, NotFoundExcetion
from common.utils import get_error_message
from services.user.main import UserService

import jwt
from config import settings

authRouter = APIRouter()

class UserAuthRequest(BaseModel):
    username: str
    password: str


@authRouter.post("/")
def log_in(reqBody: UserAuthRequest):
    userService = UserService()

    try:
        user = userService.validate_user_credentials(reqBody.username, reqBody.password)
        return {"jwt":jwt.encode(user, settings.get("SECRET"), "HS256")}
    except InvalidCredentialsException as e:
        raise HTTPException(403, get_error_message(e, "Invalid credentials"))
    except NotFoundExcetion as e:
        raise HTTPException(400, get_error_message(e, "User not found"))
    except Exception as e:
        raise HTTPException(500, "Something went wrong")