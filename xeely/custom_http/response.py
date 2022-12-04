from dataclasses import dataclass


@dataclass(frozen=True)
class HTTPResponse:
    status_code: int
    body: str
