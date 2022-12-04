class ClientTimeoutException(Exception):
    def __init__(self):
        super().__init__("Timeout occurred during request")
