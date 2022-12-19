import socket
import threading
from contextlib import contextmanager
from dataclasses import dataclass
from functools import partial
from http.server import HTTPServer
from http.server import SimpleHTTPRequestHandler
from typing import List
from typing import Optional

from xeely import console
from xeely import RESOURCES_PATH


@dataclass
class LogsManager:
    _logs: List[str]
    _instance: Optional["LogsManager"] = None

    def add_log(self, log: str):
        self._logs.append(log)

    def get_latest_log(self) -> Optional[str]:
        return None if len(self._logs) == 0 else self._logs[-1]

    @staticmethod
    def get_instance() -> "LogsManager":
        if LogsManager._instance is None:
            LogsManager._instance = LogsManager([])
        return LogsManager._instance


class RequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        request: socket.socket = self.request

        console.print_info(f"Receiving request from {request.getpeername()[0]}: {self.requestline}")
        LogsManager.get_instance().add_log(self.requestline)
        super().do_GET()


def serve_forever(httpd: HTTPServer):
    # Handling server close automatically

    with httpd:
        httpd.serve_forever()
        console.print_info("Closing HTTP Server")


@contextmanager
def run_http_server(lhost: str, lport: int):
    constructor_handler = partial(RequestHandler, directory=RESOURCES_PATH)
    httpd = HTTPServer((lhost, lport), constructor_handler, False)
    error_detected = False
    try:
        httpd.server_bind()

        httpd.server_activate()
        console.print_info(f"Running HTTP server on port: {lport}")

        thread = threading.Thread(target=serve_forever, args=(httpd,))
        # Setting the thread to be deleted when main thread is deleted
        thread.daemon = True
        thread.start()

        yield
    except OSError:
        console.print_error(f"Cannot bind HTTP Server on port {lport}")
        error_detected = True
    finally:
        if error_detected:
            exit(1)
        else:
            httpd.shutdown()


@dataclass
class HTTPServerParams:
    def __init__(self, lhost: str, lport: int):
        self._lhost = lhost
        self._lport = lport

    def get_host(self) -> str:
        return self._lhost

    def get_port(self) -> int:
        return self._lport

    def get_base_url(self) -> str:
        return f"http://{self._lhost}:{self._lport}"
