from more.cerberus.validator import CerberusValidator


class TestCerberusValidator:
    """Test suite for CerberusValidator with custom error messages and placeholders."""

    # Basic validation tests

    def test_simple_validation_with_custom_message(self):
        """Test basic validation with custom error message."""
        schema = {"name": {"type": "string", "required": True}}
        message_mapping = {"required": "Field {field} is mandatory!"}

        validator = CerberusValidator(schema, message_mapping=message_mapping)
        validator.validate({})

        assert validator.errors == {"name": ["Field name is mandatory!"]}

    def test_translation_function(self):
        """Test that translation function is applied to messages."""
        schema = {"age": {"type": "integer", "min": 18}}
        message_mapping = {"min": "Must be at least {constraint}"}

        # Simple translation function that adds a prefix
        def translator(text):
            return f"ERROR: {text}"

        validator = CerberusValidator(
            schema, message_mapping=message_mapping, translator_func=translator
        )
        validator.validate({"age": 15})

        assert validator.errors == {"age": ["ERROR: Must be at least 18"]}

    def test_nested_schema_validation(self):
        """Test validation with nested schemas."""
        schema = {
            "person": {
                "type": "dict",
                "schema": {
                    "name": {"type": "string", "required": True},
                    "age": {"type": "integer", "min": 18},
                },
            }
        }
        message_mapping = {
            "required": "Field {field} must be provided",
            "min": "Value must be at least {constraint}",
        }

        validator = CerberusValidator(schema, message_mapping=message_mapping)
        validator.validate({"person": {"age": 15}})

        # Check both nested errors are properly formatted
        assert "Value must be at least 18" in validator.errors["person"][0]["age"]
        assert "Field name must be provided" in validator.errors["person"][0]["name"]

    def test_list_of_dicts_validation(self):
        """Test validation of a list of dictionaries."""
        schema = {
            "users": {
                "type": "list",
                "schema": {
                    "type": "dict",
                    "schema": {
                        "name": {"type": "string", "required": True},
                        "email": {"type": "string", "regex": r"^[^@]+@[^@]+\.[^@]+$"},
                    },
                },
            }
        }
        message_mapping = {
            "required": "Field {field} is required",
            "regex": "Invalid email format",
        }

        validator = CerberusValidator(schema, message_mapping=message_mapping)
        validator.validate(
            {"users": [{"name": "John"}, {"name": "Jane", "email": "invalid-email"}]}
        )

        # Test that list item errors are properly captured
        assert "users" in validator.errors
        assert "Invalid email format" in str(validator.errors["users"])

    def test_logical_validation_errors(self):
        """Test validation with logical operators (anyof, allof, etc.)."""
        schema = {
            "field": {
                "anyof": [
                    {"type": "integer", "min": 10},
                    {"type": "string", "minlength": 5},
                ]
            }
        }
        message_mapping = {
            "anyof": "Value doesn't match any of the accepted formats",
            "min": "Must be at least {constraint}",
            "minlength": "Must be at least {constraint} characters",
        }

        validator = CerberusValidator(schema, message_mapping=message_mapping)
        validator.validate({"field": "abc"})

        # Test that logical error messages are properly formatted
        assert "field" in validator.errors
        assert (
            "Value doesn't match any of the accepted formats"
            in validator.errors["field"][0]
        )

    def test_dependencies_validation(self):
        """Test validation with dependencies rule."""
        schema = {
            "credit_card": {"type": "string"},
            "billing_address": {"type": "string", "dependencies": "credit_card"},
        }
        message_mapping = {"dependencies": "Field {field} depends on {constraint}"}

        validator = CerberusValidator(schema, message_mapping=message_mapping)
        validator.validate({"billing_address": "123 Main St"})

        assert "billing_address" in validator.errors
        assert "credit_card" in validator.errors["billing_address"][0]

    def test_complex_data_structure(self):
        """Test validation with a complex data structure."""
        schema = {
            "product": {
                "type": "dict",
                "schema": {
                    "name": {"type": "string", "required": True},
                    "price": {"type": "float", "min": 0},
                    "tags": {"type": "list", "schema": {"type": "string"}},
                    "variants": {
                        "type": "list",
                        "schema": {
                            "type": "dict",
                            "schema": {
                                "sku": {"type": "string", "required": True},
                                "stock": {"type": "integer", "min": 0},
                            },
                        },
                    },
                },
            }
        }
        message_mapping = {
            "required": "{field} is required",
            "min": "Value must be at least {constraint}",
        }

        data = {
            "product": {
                "name": "Test Product",
                "price": -1,
                "tags": ["tag1", 123],  # 123 is not a string
                "variants": [
                    {"stock": -5},  # missing sku, negative stock
                    {"sku": "ABC123", "stock": 10},  # valid
                ],
            }
        }

        validator = CerberusValidator(schema, message_mapping=message_mapping)
        validator.validate(data)

        # Check that complex nested errors are properly formatted
        assert "product" in validator.errors
        errors_str = str(validator.errors["product"])
        assert "Value must be at least 0" in errors_str  # for price
        assert "sku is required" in errors_str  # for first variant
        assert "Value must be at least 0" in errors_str  # for stock in first variant

    def test_value_placeholder(self):
        """Test that the {value} placeholder works properly in different validation rules."""
        schema = {
            "name": {"type": "string", "minlength": 3, "maxlength": 10},
            "age": {"type": "integer", "min": 18, "max": 65},
            "email": {"type": "string", "regex": r"^[^@]+@[^@]+\.[^@]+$"},
            "category": {"type": ["string", "integer"]},
        }

        message_mapping = {
            "type": (
                "Field '{field}' contains value '{value}' "
                "which must be of {constraint} type"
            ),
            "min": "'{value}' is below minimum value of {constraint}",
            "max": "'{value}' exceeds maximum value of {constraint}",
            "minlength": "'{value}' is too short (min {constraint} characters)",
            "maxlength": "'{value}' is too long (max {constraint} characters)",
            "regex": "'{value}' is not a valid format",
        }

        validator = CerberusValidator(schema, message_mapping=message_mapping)

        # Test min rule - numeric value
        document = {"age": 15}
        validator.validate(document)
        assert "age" in validator.errors
        error_message = str(validator.errors["age"][0])
        assert "'15' is below minimum value of 18" in error_message

        # Test max rule - numeric value
        document = {"age": 70}
        validator.validate(document)
        assert "age" in validator.errors
        error_message = str(validator.errors["age"][0])
        assert "'70' exceeds maximum value of 65" in error_message

        # Test minlength rule - string value
        document = {"name": "Jo"}
        validator.validate(document)
        assert "name" in validator.errors
        error_message = str(validator.errors["name"][0])
        assert "'Jo' is too short (min 3 characters)" in error_message

        # Test maxlength rule - string value
        document = {"name": "ThisIsTooLong"}
        validator.validate(document)
        assert "name" in validator.errors
        error_message = str(validator.errors["name"][0])
        assert "'ThisIsTooLong' is too long (max 10 characters)" in error_message

        # Test regex rule - string value
        document = {"email": "invalid-email"}
        validator.validate(document)
        assert "email" in validator.errors
        error_message = str(validator.errors["email"][0])
        assert "'invalid-email' is not a valid format" in error_message

        # Test type rule - wrong type value
        document = {"category": [1, 2, 3]}  # List, not string or integer
        validator.validate(document)
        assert "category" in validator.errors
        error_message = str(validator.errors["category"][0])
        assert "Field 'category' contains value" in error_message
        assert "must be of ['string', 'integer'] type" in error_message

    def test_value_placeholder_with_translation(self):
        """Test that the {value} placeholder works with translation."""
        schema = {"age": {"type": "integer", "min": 18}}
        min_template = "Value '{value}' is too young (min {constraint})"
        message_mapping = {"min": min_template}

        def translator(text):
            translations = {
                min_template: "Wert '{value}' ist zu jung (min {constraint})"
            }
            return translations.get(text, text)

        validator = CerberusValidator(
            schema, message_mapping=message_mapping, translator_func=translator
        )

        document = {"age": 15}
        validator.validate(document)
        assert "age" in validator.errors
        error_message = str(validator.errors["age"][0])
        assert "Wert '15' ist zu jung (min 18)" in error_message

    def test_value_placeholder_in_nested_structures(self):
        """Test that the {value} placeholder works in nested structures."""
        schema = {
            "person": {
                "type": "dict",
                "schema": {
                    "name": {"type": "string", "minlength": 3},
                    "age": {"type": "integer", "min": 18},
                },
            }
        }

        message_mapping = {
            "min": "Value '{value}' is below minimum of {constraint}",
            "minlength": "String '{value}' is too short (min {constraint})",
        }

        validator = CerberusValidator(schema, message_mapping=message_mapping)

        document = {"person": {"name": "Jo", "age": 15}}
        validator.validate(document)

        assert "person" in validator.errors
        error_str = str(validator.errors["person"])

        # Check if both error messages with values are present
        assert "String 'Jo' is too short" in error_str
        assert "Value '15' is below minimum of 18" in error_str

    def test_fallback_formatting(self):
        """Test fallback formatting when standard formatting fails."""
        schema = {"age": {"type": "integer", "min": 18}}

        # This message has invalid format placeholders - will cause format() to fail
        message_mapping = {"min": "Value is {constraint} but needs {invalid}"}

        validator = CerberusValidator(schema, message_mapping=message_mapping)

        document = {"age": 15}
        validator.validate(document)

        assert "age" in validator.errors
        error_message = str(validator.errors["age"][0])

        # After fallback formatting, we should see the constraint value
        # but the {invalid} placeholder remains unchanged
        assert "Value is 18 but needs {invalid}" in error_message
