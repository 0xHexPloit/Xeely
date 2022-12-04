class NotTextElement(Exception):
    def __init__(self):
        super().__init__("This XML node is not a Text node")
