from cerberus import Validator
from cerberus.errors import BasicErrorHandler


class TranslationErrorHandler(BasicErrorHandler):
    """Custom error handler that extends BasicErrorHandler with translation support
    and custom message mapping capabilities.

    This handler allows users to:
    - Define custom error messages for each validation rule
    - Apply translations to error messages via a callable translator function
    - Format error messages with field names, constraint values, and input values
    """

    def __init__(self, tree=None, message_mapping=None, translator_func=None):
        """Initialize the TranslationErrorHandler.

        Args:
            tree: Error tree structure from parent class
            message_mapping: Dictionary mapping rule names to custom message templates
            translator_func: Callable function for translating messages
        """
        super().__init__(tree=tree)
        self.message_mapping = message_mapping or {}
        self.translator_func = translator_func
        self.custom_messages = {}

        # Set up custom messages
        if self.message_mapping:
            for rule, message in self.message_mapping.items():
                self.custom_messages[rule] = message

    def _format_message(self, field, error):
        """Format an error message with translation support.

        First tries to use custom message templates if defined for this error rule.
        Falls back to standard Cerberus messages with translation applied.

        Args:
            field: The field name related to the error
            error: The validation error object

        Returns:
            A formatted error message string
        """
        # Use custom message if available for this rule
        if error.rule and error.rule in self.custom_messages:
            message_template = self.custom_messages[error.rule]

            # Apply translation if available
            if self.translator_func and callable(self.translator_func):
                message_template = self.translator_func(message_template)

            # Format with placeholders
            try:
                # 1. Try with named parameters
                message = message_template.format(
                    field=field, constraint=error.constraint, value=error.value
                )
            except (KeyError, ValueError, IndexError):
                try:
                    # 2. Try with positional parameters
                    if "{0}" in message_template and error.constraint is not None:
                        message = message_template.format(error.constraint, error.value)
                    elif error.info:
                        # Use error.info tuple for positional formatting
                        message = message_template.format(*error.info)
                    else:
                        # 3. Fall back to simple string replacement
                        message = message_template
                        if "{field}" in message:
                            message = message.replace("{field}", str(field))
                        if "{constraint}" in message and error.constraint is not None:
                            message = message.replace(
                                "{constraint}", str(error.constraint)
                            )
                        if "{value}" in message and error.value is not None:
                            message = message.replace("{value}", str(error.value))
                except Exception:
                    # 4. Return the raw message template
                    message = message_template

            return message

        try:
            # Get the formatted message from parent implementation first
            original_message = super()._format_message(field, error)

            # Apply translation to the full message
            if self.translator_func and callable(self.translator_func):
                translated_message = self.translator_func(original_message)
                return translated_message

            return original_message
        except Exception:
            # Fall back to a basic message if all else fails
            if error.constraint is not None:
                return f"{field} error: {error.constraint}"
            return f"{field} error"


class CerberusValidator(Validator):
    """Extends Cerberus validator with translation and custom error messages support.

    This validator enhances Cerberus with:
    - Custom error messages with placeholders like {constraint}, {field}, and {value}
    - Translation of error messages using any callable translation function
    - Integration with Morepath request and app objects

    Example:
        >>> schema = {"name": {"type": "string", "required": True}}
        >>> message_mapping = {"required": "Field {field} is mandatory"}
        >>> validator = CerberusValidator(schema, message_mapping=message_mapping)
        >>> validator.validate({})
        False
        >>> validator.errors
        {'name': ['Field name is mandatory']}
    """

    def __init__(self, *args, **kwargs):
        """Initialize the CerberusValidator.

        Args:
            *args: Arguments passed to the parent Cerberus Validator
            **kwargs: Special keyword arguments include:
                translator_func: Callable function for translating messages
                translation_domain: Domain for translation (default: "messages")
                message_mapping: Dictionary mapping rule names to custom message templates
                request: Optional request object for integration with web frameworks
        """
        self._translator_func = kwargs.pop("translator_func", None)
        self.translation_domain = kwargs.pop("translation_domain", "messages")
        self.message_mapping = kwargs.pop("message_mapping", {})

        if "request" in kwargs:
            self.request = kwargs["request"]

        # Create our custom error handler
        self.error_handler = TranslationErrorHandler(
            message_mapping=self.message_mapping, translator_func=self._translator_func
        )

        # Remove any existing error_handler from kwargs to avoid conflicts
        if "error_handler" in kwargs:
            del kwargs["error_handler"]

        # Initialize the parent Validator with our custom error handler
        super().__init__(*args, error_handler=self.error_handler, **kwargs)

    @property
    def translator_func(self):
        """Get the translator function."""
        return self._translator_func

    @translator_func.setter
    def translator_func(self, value):
        """Set the translator function and update the error_handler.

        When the translator_func is updated, we also update it in the error_handler
        to ensure that both components use the same function.
        """
        self._translator_func = value
        if hasattr(self, "error_handler"):
            self.error_handler.translator_func = value
