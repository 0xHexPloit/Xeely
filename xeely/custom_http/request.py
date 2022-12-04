from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import NewType

from xeely.custom_http.errors import HTTPFieldMissingException
from xeely.custom_http.errors import HTTPRequestParsingException
from xeely.custom_http.methods import HTTPMethods

Headers = NewType("Headers", Dict[str, str])


@dataclass(frozen=True)
class HTTPRequest:
    method: HTTPMethods
    path: str
    headers: Headers
    body: str
    protocol: str = "HTTP"

    def get_url(self) -> str:
        url = f"{self.protocol.lower()}://"
        host = self.headers.get("Host")

        if host is None:
            raise HTTPFieldMissingException("Host")
        url += str(host).strip()
        url += self.path

        return url

    @staticmethod
    def parse_request(raw_data: str) -> "HTTPRequest":
        # Splitting and removing the first line containing the HTTP
        # method used as well as the path and  HTTP version
        sep = "\n"
        request_data = raw_data.split(sep)

        # Checking first line
        first_line_data: List[str] = request_data[0].split(" ")

        if len(first_line_data) != 3:
            raise HTTPRequestParsingException()

        method_raw, path, _ = first_line_data

        # Checking path
        if path[0] != "/":
            raise HTTPRequestParsingException()

        # Checking http method
        method = HTTPMethods.get_method_from_raw_data(method_raw)
        if method is None:
            raise HTTPRequestParsingException()

        # Determining the line number from which the body part starts
        body_line_num = 0

        for idx, line in enumerate(request_data[1:]):
            if ":" not in line:
                body_line_num = idx + 1
                break

        if body_line_num == 0:
            body = ""
        else:
            body = "\n".join(request_data[body_line_num:]).strip("\n")

        headers: Headers = Headers(
            {
                data[0]: ":".join(data[1:])
                for data in [field.split(":") for field in request_data[1:body_line_num]]
            }
        )

        return HTTPRequest(method=method, path=path, headers=headers, body=body)
