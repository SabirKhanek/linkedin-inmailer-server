from dotenv import load_dotenv
load_dotenv()
from linkedin_api import Linkedin
from requests.cookies import cookiejar_from_dict
def parse_cookie_string(cookie_string):
    cookie_dict = {}
    cookies = cookie_string.split('; ')
    for cookie in cookies:
        key, value = cookie.split('=', 1)
        cookie_dict[key] = value
    return cookie_dict

import os

cookieStr = os.getenv("cookie")
if not cookieStr:
    raise Exception("Cookie string needs to be configured")
cookieObj = parse_cookie_string(cookieStr)
# print(cookieObj)
cookies = cookiejar_from_dict(
    cookieObj
)

liInstance = Linkedin("","", cookies=cookies, debug=True)
print(liInstance.send_inmail("devsabir"))
# print(liInstance.get_user_profile())

# pid = liInstance.get_profile("araffay")["profile_id"]
# salesProfile = liInstance.get_sales_profile(pid)
# salesurn = salesProfile["entityUrn"]
# print(liInstance.get_user_profile())
# print(
#     liInstance.send_sales_inmail(
#         sales_urn=salesurn, 
#         subject="I am testing", 
#         body="Please ignore", 
#         profile_id=pid
#     )
# )