class InvalidOptionException(Exception):
    def __init__(self, option: str):
        super().__init__(
            f"We could not run the attack as the value for option: {option} is invalid!"
        )
