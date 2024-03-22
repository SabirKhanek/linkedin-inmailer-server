from dotenv import load_dotenv
from os import environ
load_dotenv()


from pydantic import BaseModel

class Setting(BaseModel):
    SECRET: str = "SECRET"

settings: Setting = {
    "SECRET":environ.get("SECRET_KEY") or "SECRET"
}