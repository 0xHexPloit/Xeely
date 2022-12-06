class NoVulnerableElementFound(Exception):
    def __init__(self):
        super().__init__("Could not find a vulnerable element to perform basic attack")
