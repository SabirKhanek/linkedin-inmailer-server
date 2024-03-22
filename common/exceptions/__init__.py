class ExceptionWithStatus(Exception):
    def __init__(self, message="Internal Error", status_code=500):
        self.message = message
        self.status_code = status_code

class NotFoundExcetion(Exception):
    pass

class BadRequestException(Exception):
    pass

class InvalidCredentialsException(Exception):
    pass