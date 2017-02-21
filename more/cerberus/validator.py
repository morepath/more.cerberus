from cerberus import Validator


class CerberusValidator(Validator):
    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs['request']
        super(CerberusValidator, self).__init__(*args, **kwargs)
