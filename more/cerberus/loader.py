from functools import partial

from .validator import CerberusValidator
from .error import ValidationError


def load(schema, validator, update, request):
    if update is None:
        update = False
        if request.method == 'PUT' or request.method == 'PATCH':
            update = True
    v = validator(request=request)
    if v.validate(request.json, schema, update=update):
        return v.document
    else:
        raise ValidationError(v.errors)


def loader(schema, validator=CerberusValidator, update=None):
    """Create a load function based on schema dict and Validator class.

    :param schema: a Cerberus schema dict.
    :param validator: the validator class which must be a subclass of
        more.cerberus.CerberusValidator which is the default.
    :param update: will pass the update flag to the validator, when ``True``
        the ``required`` rules will not be checked.
        By default it will be set for PUT and PATCH requests to ``True``
        and for other requests to ``False``.

    You can plug this ``load`` function into a json view.

    Returns a ``load`` function that takes a request JSON body
    and uses the schema to validate it. This function raises
    :class:`more.cerberus.ValidationError` if validation is not successful.
    """
    if not issubclass(validator, CerberusValidator):
        raise TypeError(
            "Validator must be a subclass of more.cerberus.CerberusValidator"
        )
    return partial(load, schema, validator, update)
