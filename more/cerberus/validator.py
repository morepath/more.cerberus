from cerberus import Validator

from .error import ValidationError


class CerberusValidator(Validator):
    @property
    def request(self):
        """Add the request property to Cerberus Validator class.
        """
        return self._config.get('request', None)

    def load(self, request):
        """Load method that takes a request JSON body
        and uses the schema to validate it. The schema
        must have been provided at class instantiation.
        It raises :class:`more.cerberus.ValidationError`
        if it cannot do the validation.

        :param request: the request passed from json view.

        You can plug this ``load`` method into a json view.
        """
        self._config['request'] = request
        if self.validate(request.json):
            return self.document
        else:
            raise ValidationError(self.errors)

    def update_load(self, request):
        """Load method that takes a request JSON body
        and uses the schema to validate it. The schema
        must have been provided at class instantiation.
        ``update`` is set to ``True``, so required fields
        won't be checked.
        It raises :class:`more.cerberus.ValidationError`
        if it cannot do the validation.

        :param request: the request passed from json view.

        You can plug this ``load`` method into a json PUT or PATCH view.
        """
        self._config['request'] = request
        if self.validate(request.json, update=True):
            return self.document
        else:
            raise ValidationError(self.errors)
