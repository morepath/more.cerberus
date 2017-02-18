from webtest import TestApp as Client

from more.cerberus import (CerberusApp, CerberusValidator)


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
    v = CerberusValidator(user_schema)

    @App.path(model=User, path='/')
    def get_user():
        return user

    @App.json(model=User, request_method='POST', load=v.load)
    def user_post(self, request, json):
        for key, value in json.items():
            setattr(self, key, value)

    @App.json(model=User, request_method='PUT', load=v.update_load)
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


def test_cerberus_with_request():
    class User(object):
        def __init__(self, name=None):
            self.name = name

    user_schema = {
        'name': {
            'type': 'string'
        }
    }

    class App(CerberusApp):
        pass

    user = User()
    v = CerberusValidator(user_schema)

    @App.path(model=User, path='/')
    def get_user():
        return user

    @App.json(model=User, request_method='POST', load=v.load)
    def user_post(self, request, json):
        for key, value in json.items():
            setattr(self, key, value)

    c = Client(App())

    c.post_json('/?entry=Correct', {'name': 'Somebody'})

    assert v.request.GET['entry'] == 'Correct'
    assert user.name == 'Somebody'


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

    user_validator = CerberusValidator(user_schema)
    assert user_validator.schema == user_schema

    document_validator = CerberusValidator(document_schema)
    assert document_validator.schema == document_schema

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

    @App.json(model=User, request_method='POST', load=user_validator.load)
    def user_post(self, request, json):
        for key, value in json.items():
            setattr(self, key, value)

    @App.json(model=Document, request_method='POST',
              load=document_validator.load)
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
    v = Validator(user_schema)

    @App.path(model=User, path='/')
    def get_user():
        return user

    @App.json(model=User, request_method='POST', load=v.load)
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
    v = Validator(user_schema)

    @App.setting(section='email', name='at')
    def get_email_setting():
        return '@'

    @App.path(model=User, path='/')
    def get_user():
        return user

    @App.json(model=User, request_method='POST', load=v.load)
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
