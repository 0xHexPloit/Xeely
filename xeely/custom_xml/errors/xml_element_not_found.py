class XMLElementNotFound(Exception):
    def __init__(self):
        super().__init__("Could not find the desired element in the XML tree")
