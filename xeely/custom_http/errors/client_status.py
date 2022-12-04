class ClientStatusException(Exception):
    def __init__(self, status_code: int):
        super().__init__(f"Received status code: {status_code} !")
