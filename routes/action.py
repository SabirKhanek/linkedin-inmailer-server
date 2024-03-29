from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from services.li_clients_store import LinkedInClientStore
from services.user.main import UserService

from requests.cookies import cookiejar_from_dict

from common.utils import get_error_message
from linkedin_api import Linkedin
actionRouter = APIRouter()

liStore = LinkedInClientStore()
userService = UserService()

def get_username(req: Request):
    authUser: dict = req.session.get("user")
    if not authUser or len(authUser)==0:
        raise HTTPException(401, "User not authenticated")
    username = authUser.get("username")
    return username
    


def get_linked_in_client(req: Request):
    username = get_username(req)
    client = liStore.get_client(username)
    if not client:
        try:
            user = userService.get_user_by_username(username)
            if not user["cookie"].get("JSESSIONID") and not user["cookie"].get("li_at"):
                raise HTTPException(400, "LinkedIn session cookies are not configured!")
            
            sessionCookie = cookiejar_from_dict(user["cookie"])
            client = Linkedin("", "", cookies=sessionCookie)
            return client

        except Exception as e:
            raise HTTPException(500, get_error_message(e))


@actionRouter.get("/sales_profile")
def get_sales_profile(public_id: str, client: Linkedin=Depends(get_linked_in_client)):
    try:
        profile_id = client.get_profile(public_id).get("profile_id")
        if not profile_id:
            raise HTTPException(400, f"couldn't fetcg profile id of https://linkedin.com/in/{public_id}")
        sales_profile = client.get_sales_profile(profile_id)
        return sales_profile
    except Exception as e:
        raise HTTPException(500, get_error_message(e, "Error fetching sales profile"))
    

class InmailRequest(BaseModel):
    public_id: str
    subject: str
    body: str

@actionRouter.post("/send_inmail")
def send_inmail(body: InmailRequest, client: Linkedin=Depends(get_linked_in_client)):
    try:
        inmailResp = client.send_inmail(body.public_id, body.subject, body.body)
        return inmailResp
    except Exception as e:
        raise HTTPException(500, get_error_message(e, "Error sending inmail"))