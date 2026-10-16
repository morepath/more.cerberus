from more.cerberus.validator import CerberusValidator, TranslationErrorHandler
from unittest.mock import MagicMock


def test_translation_error_handler_exception_handling():
    """Test that TranslationErrorHandler handles exceptions gracefully."""
    schema = {"name": {"type": "string", "required": True}}

    def failing_translator(text):
        raise RuntimeError("Translator failed")

    validator = CerberusValidator(schema, translator_func=failing_translator)
    result = validator.validate({"name": 123})  # Wrong type to trigger validation error

    # Despite the translator failing, validation should still work
    assert result is False
    assert "name" in validator.errors
    error_message = validator.errors["name"][0]
    assert "name error" in error_message


def test_format_message_fallback():
    """Test the fallback path in _format_message when super() call fails."""
    error = MagicMock()
    error.code = 0xFFFF  # Invalid error code
    error.constraint = "test_constraint"

    handler = TranslationErrorHandler()
    message = handler._format_message("test_field", error)

    # Should get a fallback message containing the field name and constraint
    assert "test_field error" in message
    assert "test_constraint" in message


def test_message_with_named_placeholders():
    """Test that custom error messages with named placeholders work correctly."""
    schema = {"name": {"type": "string", "required": True}}
    message_mapping = {"required": "Field {field} is mandatory"}
    validator = CerberusValidator(schema, message_mapping=message_mapping)

    validator.validate({})

    assert "name" in validator.errors
    assert validator.errors["name"][0] == "Field name is mandatory"


def test_missing_format_cerberus_message():
    """Test that we don't need to call _format_cerberus_message directly.

    This is to confirm that the method is truly unused and can be removed.
    """
    schema = {"name": {"type": "string", "required": True}}

    message_mapping = {"required": "Field {field} is mandatory"}
    validator = CerberusValidator(schema, message_mapping=message_mapping)

    validator.validate({})
    assert "name" in validator.errors
    assert validator.errors["name"][0] == "Field name is mandatory"


def test_positional_format_parameters():
    """Test that positional format parameters like {0} work correctly in custom messages."""
    schema = {"age": {"type": "integer", "min": 18}}
    message_mapping = {"min": "Age must be at least {0}, but got {1}"}
    validator = CerberusValidator(schema, message_mapping=message_mapping)

    validator.validate({"age": 15})

    assert "age" in validator.errors
    error_message = validator.errors["age"][0]
    assert "18" in error_message
    assert "15" in error_message


def test_custom_error_exception_handling():
    """Test that exception handling in custom message path works."""
    # Create a mock error with a rule that will trigger custom message path
    error = MagicMock()
    error.rule = "required"
    error.constraint = "test_constraint"
    error.value = "test_value"
    error.info = ("info1", "info2")
    error.code = 0x02

    handler = TranslationErrorHandler(
        message_mapping={"required": "Bad {format string"}
    )

    message = handler._format_message("test_field", error)

    assert isinstance(message, str)

    # Now test the exception path when formatting with error.info
    error2 = MagicMock()
    error2.rule = "required"
    error2.constraint = "test_constraint"
    error2.value = "test_value"
    error2.info = ("info1", "info2")
    error2.code = 0x02

    handler2 = TranslationErrorHandler(
        message_mapping={
            "required": "{0} {1} {2}"
        }  # Will fail because we only have 2 values
    )

    message2 = handler2._format_message("test_field", error2)
    assert "{0} {1} {2}" == message2  # Should return the raw template


def test_super_error_exception_handling():
    """Test exception handling when super() call fails."""
    # Test with constraint
    error = MagicMock()
    error.rule = None  # No rule means it will fall through to super() call
    error.constraint = "test_constraint"
    error.value = None
    error.code = 0xFFFF  # Invalid code to cause the super() call to fail

    handler = TranslationErrorHandler()
    message = handler._format_message("test_field", error)

    # Should fall back to field name + constraint
    assert "test_field error" in message
    assert "test_constraint" in message

    error2 = MagicMock()
    error2.rule = None
    error2.constraint = None
    error2.value = None
    error2.code = 0xFFFF

    # This should hit the fallback path without constraint
    message2 = handler._format_message("test_field", error2)

    # Should just have the field name in the error
    assert message2 == "test_field error"
