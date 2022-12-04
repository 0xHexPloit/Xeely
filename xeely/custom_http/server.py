import socket
import threading
from contextlib import contextmanager
from http.server import HTTPServer
from http.server import SimpleHTTPRequestHandler
from typing import List
from typing import Optional

from xeely import console


class LogsManager:
    instance: Optional["LogsManager"] = None
    logs: List[str]

    def __init__(self):
        self.logs = []

    def add_log(self, log: str):
        self.logs.append(log)

    def get_latest_log(self) -> Optional[str]:
        return None if len(self.logs) == 0 else self.logs[-1]

    @staticmethod
    def get_instance() -> "LogsManager":
        if LogsManager.instance is None:
            LogsManager.instance = LogsManager()
        return LogsManager.instance


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
    httpd = HTTPServer((lhost, lport), RequestHandler, False)
    try:
        httpd.server_bind()
        httpd.server_activate()
        console.print_info(f"Running HTTP server on port: {lport}")

        thread = threading.Thread(target=serve_forever, args=(httpd,))
        # Setting the thread to be deleted when main thread is deleted
        thread.daemon = True
        thread.start()

        yield
    finally:
        httpd.shutdown()
