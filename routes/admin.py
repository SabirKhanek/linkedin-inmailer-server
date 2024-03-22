from common.exceptions import BadRequestException
from common.utils import get_error_message
from config import settings
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.user.main import UserService

adminRouter = APIRouter()

class AddUserRequest(BaseModel):
    username: str
    password: str
    secret: str


@adminRouter.post("/adduser")
def add_user(reqBody: AddUserRequest):
    if reqBody.secret != settings.get("SECRET"):
        raise HTTPException(401, "secret invalid")
    
    userService = UserService()
    try:
        user = userService.add_user(reqBody.username, reqBody.password)
        return user
    except BadRequestException as e:
        raise HTTPException(400,get_error_message(e, "Error adding user"))
    