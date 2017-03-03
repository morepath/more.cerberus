from webtest import TestApp as Client
import pytest

from more.cerberus import CerberusApp, CerberusValidator, loader


def test_cerberus():
    class User(object):
        def __init__(self, name=None, age=None):
            self.name = name
            self.age = age

    user_schema = {
        'name': {
            'type': 'string',
            'minlength': 3,
            'required': True
        },
        'age': {
            'type': 'integer',
            'min': 10,
            'required': True
        }
    }

    class App(CerberusApp):
        pass

    user = User()

    @App.path(model=User, path='/')
    def get_user():
        return user

    @App.json(model=User, request_method='POST', load=loader(user_schema))
    def user_post(self, request, json):
        for key, value in json.items():
            setattr(self, key, value)

    @App.json(model=User, request_method='PUT', load=loader(user_schema))
    def user_put(self, request, json):
        for key, value in json.items():
            setattr(self, key, value)

    c = Client(App())

    c.post_json('/', {'name': 'Somebody', 'age': 22})
    assert user.name == 'Somebody'
    assert user.age == 22

    r = c.post_json('/', {'name': 'Another'}, status=422)
    assert r.json == {'age': ['required field']}

    c.put_json('/', {'name': 'Another'})
    assert user.name == 'Another'
    assert user.age == 22

    r = c.put_json('/', {'age': 8}, status=422)
    assert r.json == {'age': ['min value is 10']}

    r = c.put_json('/', {'name': 'An', 'age': 8}, status=422)
    assert r.json == {
        'name': ['min length is 3'],
        'age': ['min value is 10']
    }

    r = c.put_json('/', {'name': 5, 'age': '8'}, status=422)
    assert r.json == {
        'name': ['must be of string type'],
        'age': ['must be of integer type']
    }


def test_cerberus_with_different_schemas():
    user_schema = {
        'name': {
            'type': 'string',
            'minlength': 3,
            'required': True
        },
        'age': {
            'type': 'integer',
            'min': 10,
            'required': True
        }
    }

    document_schema = {
        'title': {
            'type': 'string',
            'required': True
        },
        'author': {
            'type': 'string',
            'required': True
        }
    }

    class User(object):
        def __init__(self, name=None, age=None):
            self.name = name
            self.age = age

    class Document(object):
        def __init__(self, title=None, author=None):
            self.title = title
            self.author = author

    class App(CerberusApp):
        pass

    user = User()
    document = Document()

    @App.path(model=User, path='/user')
    def get_user():
        return user

    @App.path(model=Document, path='/document')
    def get_document():
        return document

    @App.json(model=User, request_method='POST', load=loader(user_schema))
    def user_post(self, request, json):
        for key, value in json.items():
            setattr(self, key, value)

    @App.json(model=Document, request_method='POST',
              load=loader(document_schema))
    def document_post(self, request, json):
        for key, value in json.items():
            setattr(self, key, value)

    c = Client(App())

    c.post_json('/user', {'name': 'Somebody', 'age': 22})
    assert user.name == 'Somebody'
    assert user.age == 22

    c.post_json('/document', {'title': 'Something', 'author': 'Somebody'})
    assert document.title == 'Something'
    assert document.author == 'Somebody'


def test_custom_validator():
    class User(object):
        def __init__(self, name=None, email=None):
            self.name = name
            self.email = email

    class Validator(CerberusValidator):
        def _validator_validate_email(self, field, value):
            if '@' not in value:
                self._error(field, 'Not valid email')

        def _normalize_coerce_normalize_email(self, value):
            return value.lower()

    user_schema = {
        'name': {
            'type': 'string',
            'required': True
        },
        'email': {
            'type': 'string',
            'validator': 'validate_email',
            'coerce': 'normalize_email',
            'required': True
        }
    }

    class App(CerberusApp):
        pass

    user = User()

    @App.path(model=User, path='/')
    def get_user():
        return user

    @App.json(model=User, request_method='POST',
              load=loader(user_schema, Validator))
    def user_post(self, request, json):
        for key, value in json.items():
            setattr(self, key, value)

    c = Client(App())

    c.post_json('/', {'name': 'Somebody', 'email': 'SOMEBODY@Example.COM'})

    assert user.name == 'Somebody'
    assert user.email == 'somebody@example.com'

    r = c.post_json(
        '/',
        {'name': 'Somebody', 'email': 'wrong.email.com'},
        status=422
    )

    assert r.json == {'email': ['Not valid email']}

    with pytest.raises(TypeError) as excinfo:
        loader(user_schema, validator=User)
    assert ('Validator must be a subclass of more.cerberus.CerberusValidator'
            in str(excinfo.value))


def test_custom_validator_with_request():
    class User(object):
        def __init__(self, name=None, email=None):
            self.name = name
            self.email = email

    class Validator(CerberusValidator):
        def _validator_validate_email(self, field, value):
            if self.request.app.settings.email.at not in value:
                self._error(field, 'Not valid email')

    user_schema = {
        'name': {
            'type': 'string',
            'required': True
        },
        'email': {
            'type': 'string',
            'validator': 'validate_email',
            'required': True
        }
    }

    class App(CerberusApp):
        pass

    user = User()

    @App.setting(section='email', name='at')
    def get_email_setting():
        return '@'

    @App.path(model=User, path='/')
    def get_user():
        return user

    @App.json(model=User, request_method='POST',
              load=loader(user_schema, Validator))
    def user_post(self, request, json):
        for key, value in json.items():
            setattr(self, key, value)

    c = Client(App())

    r = c.post_json(
        '/',
        {'name': 'Somebody', 'email': 'notvalid.email.com'},
        status=422
    )

    assert r.json == {'email': ['Not valid email']}
