# Linkedin inmailer server
This repository is an API wrapper around original [linkedin_api](https://github.com/tomquirk/linkedin-api) with some customized funtionalities for inmail. The original repository didn't have support for premium account capabilities. But it had good session management so it was a good repo to fork.
Directory in this repository [linkedin_api](https://github.com/SabirKhanek/linkedin-inmailer-server/tree/main/linkedin_api) contains code from original repository + Customization to enable premium account features for now Inmails.

Each premium plan has different place to send inmails i.e., Sales Navigation, Recruiter Panel in case of recruiter subscription.

So the library had to be inelligent enough to opt inmail method according to the appropriate setting.

How we did that? for that we need to dive a little bit in original repository. You can refer to original documentation to get better understanding of how things work.

Basic snippet of how the code worked in case we have raw credentials (No 2FA works in this case):

```python
from linkedin_api import Linkedin

# Authenticate using any Linkedin account credentials
api = Linkedin('reedhoffman@linkedin.com', '*******')

# GET a profile
profile = api.get_profile('billy-g')

# GET a profiles contact info
contact_info = api.get_profile_contact_info('billy-g')

# GET 1st degree connections of a given profile
connections = api.get_profile_connections('1234asc12304')
```

this Linkedin constructor returns the instance from where we have all the methods of the operations we can perform.

In our case we didn't have the option to enter raw credentials. so we were bound to choose cookie as authentication means. To make it possible here's a simple snippet:

```python
# load cookie value from env
from dotenv import load_dotenv
load_dotenv()

from linkedin_api import Linkedin

# utility function to convert raw cookie string in a cookie jar which was required by original constructor
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

cookies = cookiejar_from_dict(
    cookieObj
)

# initiating the linkedin instance
liInstance = Linkedin("","", cookies=cookies, debug=True)

# send inmail
liInstance.send_inmail("devsabir", "test inail subject", "test inmail body")
```

Here's the breakdown of parameters passed to send_inmail method

1. `devsabir` is account's public_id i.e. in, https://linkedin.com/li/devsabir
2. Inmail subject
3. Inmail body

Notice that we didn't specify which method to use (according to the premium account cookie we set.). The constructor will automatically do some magic to check if the cookies were valid and if account had premium access. If the account dont have ability to send inmails an error will be thrown.

What's the magic i am talking about?

## How it works

Let's talk about how it work. We get all the page instance id and tracking data by fetching a fresh page when the object is initialized. It will get stored in the session.

So let's say when we send a message with our object. Requests to linked in api will be made as it was sent from the official site, and the linked in api will recognize the instance ids we fetched from server prior during initialization.

This so called magic is done in [/linkedin_api/client.py](https://github.com/SabirKhanek/linkedin-inmailer-server/blob/main/linkedin_api/client.py) `Client._fetch_metadata()`.

What we customized in the method is to also detect premium subscription based on the criteria we deduced manually by inspecting the linkedin pages ourselves.

Below is the snippet:

```python
# Test if account has ssales nav
if self.SALES_NAV_BASE_URL in soup.text:
    self.metadata["premium"] = {"plan": "sales"}
    self.logger.debug("Sales subscription in account detected")
    sleep(random.randint(2, 5))
    self._fetch_sales_nav_metadata()
# Test if account has career plan
elif "urn:li:group:3926212" in soup.text:
    self.metadata["premium"] = {"plan":"career"}
    self.logger.debug("Career subscription detected")
# Test if account has recruiter plan
elif "Recruiter Account" in soup.text:
    self.metadata["premium"] = {"plan":"recruiter"}
    self.logger.debug("Recruiter account detected")
```

Refer to the file above to get the full picture of what was done.

To add inmail functionality we had to learn how linkedin send inmails officially. That is to learn which APIs they use in the process.

We added these functions for each plan as a function in the class where all other method resided. You may refer to the file where this is defined: [linkedin.py](https://github.com/SabirKhanek/linkedin-inmailer-server/blob/main/linkedin_api/linkedin.py)

We implenented these method:

1. `send_sales_inmail`: Sales Nav subscription
2. `send_recruiter_inmail`: Recruiter subscription
3. `send_career_inmail`: Career Subscription

But in runtime we had to decide which method to use based on the premium subscription the account had.

so we implemented a single method to handle the request abstracting the underlying complexity.
Below is the implementation:

```python
def send_inmail(self, public_id: str, subject="Inmail Subject", body="Inmail Body",evade=default_evade):
    profile_id = self.get_profile(public_id).get("profile_id")
    if not profile_id:
        raise HTTPException(400, f"couldn't fetch profile id of https://linkedin.com/in/{public_id}")

    premium_obj: dict = self.client.metadata.get("premium")
    if(not premium_obj):
        raise HTTPException(400, "There is no premium subscription!")

    premium_plan = premium_obj.get("plan")
        inmail_funct=None

    if premium_plan == "sales":
        inmail_funct=self.send_sales_inmail
    elif premium_plan == "career":
        inmail_funct = self.send_career_inmail
    elif premium_plan == "recruiter":
        inmail_funct = self.send_recruiter_inmail


    return {"type":premium_plan, "response":inmail_funct(profile_id, subject, body, evade, public_id=public_id)}
```

This was all about the lower level implementation.
This repository wraps this in an API layer. This api is being used by the frontend which provides nice UI to perform the operations.

Technology stack:

- **FastAPI**: For HTTP server
- **SQLModel**: ORM for database operations (database is mainly used for user controls and storing cookies per user)
- **ReactJS**: Frontend UI [Repository](https://github.com/SabirKhanek/linkedin-inmailer-ui)

## How to setup locally
### Prequisites
- Python installed in your system
### Steps
1. Clone this repository
```shell
git clone https://github.com/sabirkhanek/linkedin-inmailer-server
```
2. Install ```virtualenv```:
```bash
pip install virtualenv
```
3. create virtualenv:
```shell
virtualenv linkedin-inmailer-server
cd linkedin-inmailer-server
```
4. activate virtual environment:
On linux:
```shell
source ./bin/activate
```
On windows:
```cmd
Scripts\activate
```
5. Install dependencies
```shell
pip install -r requirements.txt
```
6. Run the server
```shell
uvicorn server:app
```
The server will start listening on port 8000
7. Open the app interface
```
http://localhost:8000/app
```
Static bundle for ui is served from app directory. It was added for convenience. You can check the code for frontend [here](https://github.com/sabirkhanek/linkedin-inmailer-ui). 