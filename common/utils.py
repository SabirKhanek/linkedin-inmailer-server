def get_error_message(e: Exception, default="Error") -> str:
    try:
        return e.args[0]
    except (IndexError, AttributeError):
        return default

def parse_cookie_string(cookie_string: str):
    cookie_dict = {}
    cookies = cookie_string.split('; ')
    for cookie in cookies:
        key, value = cookie.split('=', 1)
        cookie_dict[key] = value
    return cookie_dict
