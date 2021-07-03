from urllib.parse import quote as _uriquote


class Route:
    BASE = "https://api-gateway.coupang.com/v2/providers/affiliate_open_api/apis/openapi/v1/"

    def __init__(self, method: str, path: str, **parameters) -> None:
        self.path: str = path
        self.method = method
        url = f"{self.BASE}{self.path}"

        if parameters:
            url = url.format_map({k: _uriquote(v) if isinstance(v, str) else v for k, v in parameters.items()})

        self.url: str = url
