class XMLDataNotFound(Exception):
    def __init__(self):
        super().__init__("Could not find XML content")
