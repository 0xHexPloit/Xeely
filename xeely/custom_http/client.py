import httpx

from xeely.custom_http.errors import ClientStatusException
from xeely.custom_http.errors import ClientTimeoutException
from xeely.custom_http.response import HTTPResponse


class HTTPClient:
    @staticmethod
    def send_post_request(url: str, data: str, *, timeout=10) -> HTTPResponse:
        try:
            http_response = httpx.post(url=url, content=data.encode("utf-8"), timeout=timeout)
            if http_response.status_code != 200:
                raise ClientStatusException(http_response.status_code)

            response_content = http_response.content.decode("utf-8")
            return HTTPResponse(status_code=http_response.status_code, body=response_content)
        except httpx.TimeoutException:
            raise ClientTimeoutException()
