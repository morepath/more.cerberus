from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Any, cast

from .error import ValidationError
from .validator import CerberusValidator

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping


def load(
    schema: Mapping[str, Any],
    validator_factory: Callable[..., CerberusValidator],
    update: bool | None,
    request: Any,
) -> dict[str, Any]:
    if update is None:
        update = False
        if request.method == "PUT" or request.method == "PATCH":
            update = True
    v = validator_factory(request=request)
    if v.validate(request.json, schema, update=update):
        return cast("dict[str, Any]", v.document)
    else:
        raise ValidationError(v.errors)


def loader(
    schema: Mapping[str, Any],
    validator: type[CerberusValidator] = CerberusValidator,
    update: bool | None = None,
    translator_func: Callable[[str], str] | None = None,
    translation_domain: str = "messages",
    message_mapping: dict[str, str] = {},
) -> Callable[[Any], dict[str, Any]]:
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
    if not issubclass(cast("type[object]", validator), CerberusValidator):
        raise TypeError(
            "Validator must be a subclass of more.cerberus.CerberusValidator"
        )

    def validator_factory(**kwargs: Any) -> CerberusValidator:
        return validator(
            translator_func=translator_func,
            translation_domain=translation_domain,
            message_mapping=message_mapping,
            **kwargs,
        )

    return partial(load, schema, validator_factory, update)
