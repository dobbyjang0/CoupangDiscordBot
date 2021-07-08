class Forbidden(Exception):
    pass


class CoupangException(Exception):
    pass


class InvalidSignature(CoupangException):

    def __init__(self):
        message = 'Invalid signature'
        super().__init__(message)
