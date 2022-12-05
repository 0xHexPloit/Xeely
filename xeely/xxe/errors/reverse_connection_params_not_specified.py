class ReverseConnectionParamsNotSpecified(Exception):
    def __init__(self):
        super().__init__(
            "Cannot run the attack as reverse connection parameters are not specified!"
        )
