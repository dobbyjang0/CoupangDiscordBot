from aiohttp import ClientResponse
from typing import Optional, Union, Dict, Any


class Forbidden(Exception):
    pass


class NotFound(Exception):
    pass


class CoupangException(Exception):

    def __init__(self, response: ClientResponse, message: Optional[Union[str, Dict[str, Any]]]):
        self.response: ClientResponse = response
        self.status: int = response.status

        self.code: int
        self.text: str

        if isinstance(message, dict):
            self.code = message.get('rCode', 0)
            self.text = message.get('rMessage', '')

        else:
            self.text = message or ''
            self.code = 0

        fmt = '{0.status} {0.reason} (error code: {1})'

        if len(self.text):
            fmt += ': {2}'

        super().__init__(fmt.format(self.response, self.code, self.text))


class InvalidSignature(CoupangException):
    pass
