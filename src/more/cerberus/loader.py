from functools import partial

from .validator import CerberusValidator
from .error import ValidationError


def load(schema, validator_factory, update, request):
    if update is None:
        update = False
        if request.method == "PUT" or request.method == "PATCH":
            update = True
    v = validator_factory(request=request)
    if v.validate(request.json, schema, update=update):
        return v.document
    else:
        raise ValidationError(v.errors)


def loader(
    schema,
    validator=CerberusValidator,
    update=None,
    translator_func=None,
    translation_domain="messages",
    message_mapping=None,
):
    """Create a load function based on schema dict and Validator class.

    :param schema: a Cerberus schema dict.
    :param validator: the validator class which must be a subclass of
        more.cerberus.CerberusValidator which is the default.
    :param update: will pass the update flag to the validator, when ``True``
        the ``required`` rules will not be checked.
        By default it will be set for PUT and PATCH requests to ``True``
        and for other requests to ``False``.
    :param translator_func: a function that takes a message string and returns
        the translated string (e.g., lazy_gettext)
    :param translation_domain: the domain/namespace for translations (optional)
    :param message_mapping: a dictionary mapping validation rules to custom messages

    You can plug this ``load`` function into a json view.

    Returns a ``load`` function that takes a request JSON body
    and uses the schema to validate it. This function raises
    :class:`more.cerberus.ValidationError` if validation is not successful.
    """
    if not issubclass(validator, CerberusValidator):
        raise TypeError(
            "Validator must be a subclass of more.cerberus.CerberusValidator"
        )

    def validator_factory(**kwargs):
        return validator(
            translator_func=translator_func,
            translation_domain=translation_domain,
            message_mapping=message_mapping,
            **kwargs
        )

    return partial(load, schema, validator_factory, update)
