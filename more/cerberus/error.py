class ValidationError(Exception):
    def __init__(self, errors):
        super().__init__("Cerberus validation error")
        self.errors = errors
