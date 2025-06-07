from webtest import TestApp as Client
from more.cerberus import CerberusApp, CerberusValidator, loader


def mock_translator(text):
    """Mock translator function that simulates a gettext implementation"""
    translations = {
        # Custom messages with placeholders
        "field is required": "Pflichtfeld",
        "min value is {constraint}": "Minimalwert ist {constraint}",
        "max length is {constraint}": "Maximallänge ist {constraint}",
        "min length is {constraint}": "Minimallänge ist {constraint}",
        "invalid format": "Ungültiges Format",
        "must be of integer type": "muss ein Integer sein",
        "must be of {constraint} type": "muss ein {constraint} sein",
        "Value must not exceed {constraint}": "Wert darf {constraint} nicht überschreiten",
        # Default Cerberus error messages
        "required field": "Pflichtfeld",
        "min value is 10": "Minimalwert ist 10",
        "min length is 3": "Minimallänge ist 3",
    }
    return translations.get(text, text)


# Core functionality tests
def test_translation():
    """Test that custom error messages with placeholders are properly translated"""

    class User:
        def __init__(self, name=None, age=None, email=None):
            self.name = name
            self.age = age
            self.email = email

    user_schema = {
        "name": {"type": "string", "minlength": 3, "required": True},
        "age": {"type": "integer", "min": 10, "required": True},
        "email": {
            "type": "string",
            "regex": r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
        },
    }

    # Define custom error messages
    message_mapping = {
        "required": "required field",
        "min": "min value is {constraint}",
        "minlength": "min length is {constraint}",
        "maxlength": "max length is {constraint}",
        "regex": "invalid format",
    }

    class App(CerberusApp):
        pass

    user = User()

    @App.path(model=User, path="/")
    def get_user():
        return user

    @App.json(
        model=User,
        request_method="POST",
        load=loader(
            user_schema,
            translator_func=mock_translator,
            message_mapping=message_mapping,
        ),
    )
    def user_post(self, request, json):
        for key, value in json.items():
            setattr(self, key, value)

    c = Client(App())
    # Test translated required field error
    r = c.post_json("/", {"name": "Joe"}, status=422)
    assert r.json == {"age": ["Pflichtfeld"]}

    # Test translated min value error
    r = c.post_json("/", {"name": "Joe", "age": 5}, status=422)
    assert r.json == {"age": ["Minimalwert ist 10"]}

    # Test translated min length error
    r = c.post_json("/", {"name": "Jo", "age": 20}, status=422)
    assert r.json == {"name": ["Minimallänge ist 3"]}

    # Test translated regex error
    r = c.post_json(
        "/", {"name": "John", "age": 20, "email": "invalid-email"}, status=422
    )
    assert r.json == {"email": ["Ungültiges Format"]}

    # Test successful validation
    c.post_json("/", {"name": "John", "age": 20, "email": "test@example.com"})
    assert user.name == "John"
    assert user.age == 20
    assert user.email == "test@example.com"


def test_translation_without_mapping():
    """Test that translation works even without a message mapping"""

    class User:
        def __init__(self, name=None, age=None):
            self.name = name
            self.age = age

    user_schema = {
        "name": {"type": "string", "minlength": 3, "required": True},
        "age": {"type": "integer", "min": 10, "required": True},
    }

    class App(CerberusApp):
        pass

    user = User()

    @App.path(model=User, path="/")
    def get_user():
        return user

    @App.json(
        model=User,
        request_method="POST",
        load=loader(user_schema, translator_func=mock_translator),
    )
    def user_post(self, request, json):
        pass  # pragma: no cover

    c = Client(App())
    # Test if the translator function is applied to the default error messages
    r = c.post_json("/", {"name": "Jo", "age": 5}, status=422)
    assert "age" in r.json
    assert "name" in r.json


def test_message_mapping_without_translation():
    """Test that message mapping works without a translator function"""

    class User:
        def __init__(self, name=None, age=None):
            self.name = name
            self.age = age

    user_schema = {
        "name": {"type": "string", "minlength": 3, "required": True},
        "age": {"type": "integer", "min": 10, "required": True},
    }
    # Define custom error messages
    message_mapping = {
        "required": "This field is absolutely necessary",
        "min": "Value cannot be less than {constraint}",
    }

    class App(CerberusApp):
        pass

    user = User()

    @App.path(model=User, path="/")
    def get_user():
        return user

    @App.json(
        model=User,
        request_method="POST",
        load=loader(user_schema, message_mapping=message_mapping),
    )
    def user_post(self, request, json):
        pass  # pragma: no cover

    c = Client(App())
    # Test custom required field message
    r = c.post_json("/", {"name": "Joe"}, status=422)
    assert r.json == {"age": ["This field is absolutely necessary"]}

    # Test custom min value message
    r = c.post_json("/", {"name": "Joe", "age": 5}, status=422)
    assert r.json == {"age": ["Value cannot be less than 10"]}

    # Test type error
    r = c.post_json("/", {"name": "Joe", "age": "five"}, status=422)
    assert r.json == {"age": ["must be of integer type"]}


def test_minlength_validation():
    """Test that minlength validation with custom messages and placeholders works"""
    schema = {"name": {"type": "string", "minlength": 3}}
    message_mapping = {"minlength": "min length is {constraint}"}

    # Create validator with custom message mapping and translator
    validator = CerberusValidator(
        schema, message_mapping=message_mapping, translator_func=mock_translator
    )

    # Test with a value that is too short
    document = {"name": "Jo"}  # 2 characters, below minlength of 3
    validator.validate(document)

    # Check if the error message is correct and translated
    assert "name" in validator.errors
    error_message = str(validator.errors["name"][0])
    assert "Minimallänge ist 3" in error_message

    # Test with a valid value
    document = {"name": "John"}  # 4 characters, meets minlength of 3
    result = validator.validate(document)
    assert result is True
    assert not validator.errors


def test_maxlength_validation():
    """Test that maxlength validation with custom messages and placeholders works"""
    schema = {"name": {"type": "string", "maxlength": 5}}
    message_mapping = {"maxlength": "max length is {constraint}"}

    # Create validator with custom message mapping and translator
    validator = CerberusValidator(
        schema, message_mapping=message_mapping, translator_func=mock_translator
    )

    # Test with a value that exceeds the maxlength
    document = {"name": "John Doe"}  # 8 characters, exceeds maxlength of 5
    validator.validate(document)

    # Check if the error message is correct and translated
    assert "name" in validator.errors
    error_message = str(validator.errors["name"][0])
    assert "Maximallänge ist 5" in error_message

    # Test with a valid value
    document = {"name": "John"}  # 4 characters, within maxlength of 5
    result = validator.validate(document)
    assert result is True
    assert not validator.errors


def test_max_validation():
    """Test that max validation with custom messages and placeholders works"""
    schema = {"score": {"type": "integer", "max": 100}}
    message_mapping = {"max": "Value must not exceed {constraint}"}

    # Create validator with custom message mapping and translator
    validator = CerberusValidator(
        schema, message_mapping=message_mapping, translator_func=mock_translator
    )

    # Test with a value that exceeds the maximum
    document = {"score": 150}  # Exceeds max of 100
    validator.validate(document)

    # Check if the error message is correct and translated
    assert "score" in validator.errors
    error_message = str(validator.errors["score"][0])
    assert "Wert darf 100 nicht überschreiten" in error_message

    # Test with a valid value
    document = {"score": 75}  # Within max of 100
    result = validator.validate(document)
    assert result is True
    assert not validator.errors


def test_multiple_types_validation():
    """Test validation with multiple allowed types"""
    # Schema with multiple allowed types
    schema = {"id": {"type": ["string", "integer"]}}
    message_mapping = {"type": "Must be of {constraint} type"}

    # Create validator with custom message mapping and translator
    validator = CerberusValidator(
        schema, message_mapping=message_mapping, translator_func=mock_translator
    )

    # Test with an invalid value type
    document = {"id": [1, 2, 3]}  # List type, not string or integer
    validator.validate(document)

    # Check if the error message correctly shows the allowed types
    assert "id" in validator.errors
    error_message = str(validator.errors["id"][0])
    assert "['string', 'integer']" in error_message

    # Test with valid string type
    document = {"id": "abc123"}
    assert validator.validate(document) is True

    # Test with valid integer type
    document = {"id": 12345}
    assert validator.validate(document) is True


def test_single_type_list_validation():
    """Test validation with a single type in a list"""
    # Schema with a single type in a list
    schema = {"id": {"type": ["integer"]}}
    message_mapping = {"type": "Must be of {constraint} type"}

    # Create validator with custom message mapping
    validator = CerberusValidator(schema, message_mapping=message_mapping)

    # Test with an invalid value type
    document = {"id": "abc"}  # String, not integer
    validator.validate(document)

    # Check if the error message correctly shows the single type
    assert "id" in validator.errors
    error_message = str(validator.errors["id"][0])
    assert "Must be of ['integer'] type" in error_message

    # Test with valid type
    document = {"id": 123}
    assert validator.validate(document) is True


# Tests for placeholder handling
def test_placeholder_replacement():
    """Test that all types of placeholders are properly replaced in error messages"""
    # Define a schema with various validation rules
    schema = {
        "username": {
            "type": "string",
            "minlength": 3,
            "maxlength": 20,
            "required": True,
        },
        "score": {"type": "integer", "min": 0, "max": 100},
        "category": {"type": ["string", "integer"]},  # Multiple types
    }

    # Custom messages with all placeholder types
    message_mapping = {
        "type": "Field '{field}' with value '{value}' must be of {type} type",
        "min": "Value {value} must be at least {constraint}",
        "max": "Value {value} must not exceed {constraint}",
        "minlength": "Length of '{value}' must be at least {constraint} characters",
        "maxlength": "Length of '{value}' must not exceed {constraint} characters",
    }

    # Create validator with custom message mapping
    validator = CerberusValidator(schema, message_mapping=message_mapping)

    # Test field placeholder
    document = {"category": [1, 2, 3]}
    validator.validate(document)
    error_message = str(validator.errors["category"][0])
    assert "Field 'category'" in error_message

    # Test value placeholder
    document = {"score": -10}
    validator.validate(document)
    error_message = str(validator.errors["score"][0])
    assert "Value -10 must be at least 0" in error_message

    # Test maxlength placeholder
    document = {"username": "thisisaverylongusernamethatexceedstwentycharacters"}
    validator.validate(document)
    error_message = str(validator.errors["username"][0])
    assert "must not exceed 20 characters" in error_message


# Tests for specific error handler behaviors
def test_error_info_translation():
    """Test that error messages are translated directly"""

    def translator(text):
        translations = {"required field": "Pflichtfeld"}
        return translations.get(text, text)

    schema = {"name": {"required": True}}
    document = {}  # Missing required field

    validator = CerberusValidator(schema, translator_func=translator)
    validator.validate(document)

    assert "name" in validator.errors
    error_message = str(validator.errors["name"][0])
    assert "Pflichtfeld" in error_message


def test_default_error_message_translation():
    """Test that default error messages from Cerberus are translated"""
    schema = {
        "name": {"type": "string", "minlength": 3},
        "age": {"type": "integer", "min": 10, "required": True},
    }

    # Create validator with translator
    validator = CerberusValidator(schema, translator_func=mock_translator)

    # Test required field error
    document = {"name": "Jo"}  # Missing required age field
    validator.validate(document)
    errors = validator.errors
    assert "age" in errors

    # Test type error
    document = {"name": "John", "age": "twenty"}  # Age should be integer
    validator.validate(document)
    errors = validator.errors
    assert "age" in errors
    assert errors["age"][0] == "muss ein Integer sein"

    # Test min value error
    document = {"name": "John", "age": 5}  # Age below minimum
    validator.validate(document)
    errors = validator.errors
    assert "age" in errors
    assert "Minimalwert ist 10" in errors["age"][0]

    # Test min length error
    document = {"name": "Jo", "age": 20}  # Name too short
    validator.validate(document)
    errors = validator.errors
    assert "name" in errors
    assert "Minimallänge ist 3" in errors["name"][0]


# Configuration tests
def test_message_mapping_none():
    """Test that when message_mapping is None, _set_message_mapping exits early"""
    # Create a schema for testing
    schema = {"name": {"type": "string", "required": True}}

    # First, create a validator with message_mapping=None (default)
    validator = CerberusValidator(schema)
    assert validator.message_mapping == {}

    # Create a validator with a non-None message_mapping for comparison
    message_mapping = {"required": "This field is mandatory"}
    validator_with_mapping = CerberusValidator(schema, message_mapping=message_mapping)
    assert validator_with_mapping.message_mapping == message_mapping


def test_standard_required_field_translation():
    """
    Test that default Cerberus error messages like 'field is required'
    are properly translated even when not using custom message mapping.

    This test simulates the issue encountered in washapp where the standard
    'field is required' message wasn't being translated properly.
    """
    # Define a schema with a required field
    schema = {"name": {"type": "string", "required": True}}

    # Mock gettext-style translator function similar to what's used in washapp
    def translator(text):
        translations = {
            # Standard Cerberus error message for required field
            "required field": "dieses Feld ist erforderlich",
            "must be of string type": "muss ein String sein",
        }
        return translations.get(text, text)

    # Create validator with translator function but no custom message mapping
    validator = CerberusValidator(schema, translator_func=translator)

    # Validate an empty document
    validator.validate({})

    # Check if the error message was translated
    assert "name" in validator.errors
    translated_message = str(validator.errors["name"][0])

    # This is the assertion that would fail without our fix
    assert "dieses Feld ist erforderlich" in translated_message
    assert "field is required" not in translated_message

    # Now test with a field of wrong type
    validator.validate({"name": 123})  # name should be string
    assert "name" in validator.errors
    translated_message = str(validator.errors["name"][0])
    assert "muss ein String sein" in translated_message
    assert "must be of string type" not in translated_message


def test_late_translator_assignment():
    """Test that setting translator_func after initialization works correctly.

    This test verifies the specific case that occurs in frameworks like washapp
    where the translator_func is set after the validator is created.
    """
    # Define a schema with a required field
    schema = {"name": {"type": "string", "required": True}}

    # Mock translator function
    def translator(text):
        translations = {
            "required field": "this is required now",
            "must be of string type": "must be text",
        }
        return translations.get(text, text)

    # Create validator without translator function
    validator = CerberusValidator(schema)

    # Validate a document to trigger errors
    document = {}
    validator.validate(document)

    # Errors should have standard English messages
    assert "name" in validator.errors
    assert "required field" in str(validator.errors["name"][0])

    # Now set the translator function after initialization
    validator.translator_func = translator

    # Validate again
    validator.validate(document)

    # Errors should now be translated
    assert "name" in validator.errors
    assert "this is required now" in str(validator.errors["name"][0])

    # Test that type errors are also translated after setting translator
    validator.validate({"name": 123})
    assert "name" in validator.errors
    assert "must be text" in str(validator.errors["name"][0])


def test_translator_func_getter():
    """Test that the translator_func getter property returns the correct function.

    This test ensures that the getter property for translator_func in the
    CerberusValidator class works correctly, both when the translator is set
    during initialization and when it's set later.
    """
    # Define a simple schema
    schema = {"name": {"type": "string"}}

    # Define two translator functions to test with
    def translator1(text):
        return f"T1: {text}"

    def translator2(text):
        return f"T2: {text}"

    # Test getting the translator set during initialization
    validator1 = CerberusValidator(schema, translator_func=translator1)
    assert validator1.translator_func is translator1
    assert validator1.translator_func("test") == "T1: test"

    # Test that the translator_func is correctly passed to error_handler
    assert validator1.error_handler.translator_func is translator1

    # Test that the getter returns None when no translator is set
    validator2 = CerberusValidator(schema)
    assert validator2.translator_func is None

    # Test getting the translator after setting it via the setter
    validator2.translator_func = translator2
    assert validator2.translator_func is translator2
    assert validator2.translator_func("test") == "T2: test"

    # Test that setting to None works correctly
    validator1.translator_func = None
    assert validator1.translator_func is None
