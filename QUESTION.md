## Questions

### **What's inside the cookie? What does each field mean?**

Only two of the cookies are important for linkedin session. These cookies are used for auth purpose in LinkedIn Backend. Apart from these cookies otheres are linkedin tracking cookies and are irrelevant. But it's no harm to include those as well. Just so linkedin dont detect anything.

- **li_at**
- **JSESSIONID**

[The file you mentioned](https://github.com/SabirKhanek/linkedin-inmailer-server/blob/main/routes/action.py#L60) uses FastAPI syntax. I am using FastAPI for API wrapper around linkedin. LinkedIn decorator `Linkedin=Depends(get_linked_in_client)`. is used to fetch the linkedin instance for the authenicated user. [Impementation](https://github.com/SabirKhanek/linkedin-inmailer-server/blob/main/routes/action.py#L25)

```python
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
```

LinkedIn constructor requires cookiejar object. We convert our cookie dictionary into cookiejar using this function from `requests` module: `cookiejar_from_dict`.

### What metadata does the Li Client need.

It just needs raw credentials or cookies. Going with cookies is better because 2FA is enabled on premium accounts. we get cookie string from linkedin and then convert that string into python dict

```python
def parse_cookie_string(cookie_string: str):
    cookie_dict = {}
    cookies = cookie_string.split('; ')
    for cookie in cookies:
        key, value = cookie.split('=', 1)
        cookie_dict[key] = value
    return cookie_dict
cookieObj = parse_cookie_string("li_at=your******; JSESSIONID=your******")
```

Then we convert this dict into cookiejar object:

```python
cookies = cookiejar_from_dict(
    cookieObj
)
from requests.cookies import cookiejar_from_dict
```

Then just pass the object as parameter to LinkedIn constructor

```python
liInstance = Linkedin("","", cookies=cookies, debug=True)
```

### Describe each step for `send_inmail` function

This was thoroughly explained in the [README](https://github.com/SabirKhanek/linkedin-inmailer-server) of the repository. Let me share that here as well

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

This method is defined inside the LinkedIn class. When the object is initialized it is detected which premium plan the account (of which cookies were passed as parameters). Then inmail_function is configured based on the subscription:

```python
if premium_plan == "sales":
    inmail_funct=self.send_sales_inmail
elif premium_plan == "career":
    inmail_funct = self.send_career_inmail
elif premium_plan == "recruiter":
    inmail_funct = self.send_recruiter_inmail
```

and then is called here.

```python
return {"type":premium_plan, "response":inmail_funct(profile_id, subject, body, evade, public_id=public_id)}
```

Each of the function carries out sending inmail job just as LinkedIn would have done. These function creates the request to be sent to linkedin api.

```python
def send_recruiter_inmail(self, profile_id, subject="Inmail Subject", body="Inmail Body",evade=default_evade, public_id=None):
    self.logger.debug("Sending inmail request")
    recruiter_urn_resp = self.get_recruiter_profile(profile_id)
    recruiter_urn =  recruiter_urn_resp.get("referenceUrn")
    contactInfo = recruiter_urn_resp.get("contactInfo") or {}
    email = contactInfo.get("primaryEmail") or None

    if not recruiter_urn:
        raise HTTPException(400, f"Couldn't fetch sales profile url: {json.dumps(recruiter_urn_resp)}")

    url = f"{self.client.LINKEDIN_BASE_URL}/talent/api/graphql?action=execute&queryId=talentMultiMessagePosts.be0f985141a7cf89d4d410c4e5839e8f"

    headers={
        **self.client.session.headers,
        "content-type": "application/json",
        "referer":f"{self.client.LINKEDIN_BASE_URL}/talent/profile/{profile_id}"
    }
    req_body={
        "variables":{
            "messagePostPayloads":[
                {
                    "emailAddress":email,
                    "followUpPosts":[],
                    "ofccpTrackingId":None,
                    "recipientProfileUrn":recruiter_urn,
                    "primaryPost":{
                        "attachments":[],
                        "body":"Test body",
                        "channel":"INMAIL",
                        "enableCalenderShare":False,
                        "subject":subject
                    },
                    "signature":public_id or "",
                    "visibility":"PRIVATE",
                    "globalSourcingType":"FLAGSHIP_PROFILE"
                }
            ]
        },
        "queryId":"talentMultiMessagePosts.be0f985141a7cf89d4d410c4e5839e8f",
        "includeWebMetadata":True
    }

    req_body_str = json.dumps(req_body)
    evade()
    res = requests.post(url=url, data=req_body_str, headers=headers, cookies=self.client.session.cookies)

    return res.json()
```

It was nothing just request was forged. These patterns were learnt by inspecting Network Requests from LinkedIn app.

### How often do we need to refresh the cookie?

Until you logout from the linkedin yourself or session is automatically expired.

### Please share the docs for any of the Li APIs that you used?

Well there is no official API for linkedin. I used this open source library: [linkedin-api by Tom Quirk](https://github.com/tomquirk/linkedin-api)
