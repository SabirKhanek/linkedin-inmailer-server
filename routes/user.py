import re
from typing import Dict
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, field_validator
from common.exceptions import NotFoundExcetion
from common.utils import get_error_message
from services.user.main import UserService
userRouter = APIRouter()

class LiSessionCookie(BaseModel):
    cookie: Dict[str, str]


    @field_validator('cookie')
    def validate_dict(cls, v):
        missing_keys = ["JSESSIONID", "li_at"] - v.keys()
        if missing_keys:
            raise ValueError(f"Missing required keys: {', '.join(missing_keys)}")
        return v
    
@userRouter.post("/setsession")
def set_li_session(cookies: LiSessionCookie, req: Request):
    userService = UserService()
    authUser: dict = req.session.get("user")
    if not authUser or len(authUser)==0:
        raise HTTPException(401, "User not authenticated")
    
    res = userService.add_user_cookies(authUser.get("username"), cookies.cookie)
    return res

@userRouter.get("/me")
def get_auth_user(req: Request):
    userService = UserService()
    authUser: dict = req.session.get("user")
    if not authUser or len(authUser)==0:
        raise HTTPException(401, "User not authenticated")
    
    try: 
        res = userService.get_user_by_username(authUser.get("username"))
        return res
    except NotFoundExcetion as e:
        raise HTTPException(404, get_error_message(e, "User not found"))
    except Exception as  e:
        raise HTTPException(500, get_error_message(e))
    