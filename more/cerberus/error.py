class ValidationError(Exception):
    def __init__(self, errors):
        super(ValidationError, self).__init__("Cerberus validation error")
        self.errors = errors
