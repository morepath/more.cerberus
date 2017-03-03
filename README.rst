more.cerberus: validation and normalization support for Morepath
================================================================

This package provides Morepath integration for the Cerberus_ data validation
library:

.. _Cerberus: https://python-cerberus.org

Cerberus can automate user input validation and normalization in a HTTP API.


Schema
------

You can define a schema simply as a Python dict:

.. code-block:: python

  user_schema = {
    'name': {'type': 'string', 'minlength' : 3, 'required': True},
    'age': {'type': 'integer', 'min': 0, 'required': True}
  }

Altenatively you can define the schema in yaml and load it
with pyyaml:

.. code-block:: yaml

    user:
      name:
        type: string
        minlength: 3
        required: true
      age:
        type: integer
        min: 0
        required: true


.. code-block:: python

  import yaml

  with open('schema.yml') as schema:
      schema = yaml.load(schema)

  user_schema = schema['user']


Validate
--------

The ``more.cerberus`` integration helps
with validation of the request body as it is POSTed or PUT to a view.
First we must create a loader for our schema:

.. code-block:: python

  from more.cerberus import loader

  user_schema_load = loader(user_schema)

We can use this loader to handle a PUT or POST request for instance:

.. code-block:: python

  @App.json(model=User, request_method='POST', load=user_schema_load)
  def user_post(self, request, json):
      # json is now a validated and normalized dict of whatever got
      # POST onto this view that you can use to update
      # self


Update models
-------------

By default in PUT or PATCH requests the ``load`` function
sets the ``update`` flag of the ``validate()`` method to ``True``,
so required fields won’t be checked. For other requests like
POST ``update`` is ``False``.

You can set this manually by passing the ``update`` argument
to the ``load`` function:

.. code-block:: python

  user_schema_load = loader(user_schema, update=False)

  @App.json(model=User, request_method='PUT', load=user_schema_load)
  def user_put(self, request, json):


Customize the Validator
-----------------------

With Cerberus you can customize the rules, data types, validators,
coercers (for normalization) and default setters by subclassing
CerberusValidator:

.. code-block:: python

  import re
  from more.cerberus import CerberusValidator

  class CustomValidator(CerberusValidator):
      def _validator_validate_email(self, field, value):
        match = re.match(
          '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',value
        )
        if match == None:
          self._error(field, 'Not valid email')

      def _normalize_coerce_normalize_email(self, value):
          parts = value.split('@')
          if len(parts) != 2:
            return value
          else:
            domain = parts[1].lower
            if domain == 'googlemail.com':
              domain = 'gmail.com'
            return parts[0] + '@' + domain

You have to pass the custom Validator class to the ``load`` function:

.. code-block:: python

  user_schema_load = loader(user_schema, validator=CustomValidator)

Now you can use the new email validator and normalizer in your schema:

.. code-block:: python

  user_schema = {
    'name': {'type': 'string', 'minlength' : 3, 'required': True},
    'email': {'type': 'string', 'validator': 'validate_email',
              'coerce': 'normalize_email','required': True}
  }

or with YAML:

.. code-block:: yaml

  user:
    name:
      type: string
      minlength: 3
      required: true
    email:
      type: string
      validator: validate_email
      coerce: normalize_email
      required: true

For more information how to customize the Validator take a look at the
`Cerberus documentation`_.

.. _Cerberus documentation:
    http://docs.python-cerberus.org/en/stable/customize.html


Use the request or app instance in your custom validator
--------------------------------------------------------

In ``CerberusValidator`` you can access the ``request`` through
``self.request`` and the ``app`` through ``self.request.app``.
Like this you can use e.g. Morepath settings and services when
extending rules.

Here an example from `auth-boilerplate`_ for custom email validation and
normalization using a service based on `email_validator`_:

.. _auth-boilerplate: https://github.com/yacoma/auth-boilerplate
.. _email_validator: https://github.com/JoshData/python-email-validator

.. code-block:: python

  from more.cerberus import CerberusValidator
  from email_validator import EmailSyntaxError, EmailUndeliverableError


  class Validator(CerberusValidator):
      def _validator_verify_email(self, field, value):
          email_validation_service = self.request.app.service(
              name='email_validation'
          )
          try:
              email_validation_service.verify(value)

          except EmailSyntaxError:
              self._error(field, 'Not valid email')

          except EmailUndeliverableError:
              self._error(field, 'Email could not be delivered')

      def _normalize_coerce_normalize_email(self, value):
          email_validation_service = self.request.app.service(
              name='email_validation'
          )
          return email_validation_service.normalize(value)


Error handling
--------------

If validation fails due to a validation error (a required field is
missing, or a field is of the wrong datatype, for instance), you want
to show some kind of error message. The ``load`` function created by
``more.cerberus`` raises the ``more.cerberus.ValidationError`` exception
in case of errors.

This exception object has an ``errors`` attribute with the validation errors.
You must define an exception view for it, otherwise validation errors are
returned as "500 internal server error" to API users.

This package provides a default exception view implementation. If you subclass
your application from ``more.cerberus.CerberusApp`` then you get a default
error view for ``ValidationError`` that has a 422 status code with a JSON
response with the Cerberus errors structure:

.. code-block:: python

  from more.cerberus import CerberusApp

  class App(CerberusApp):
      pass

Now your app has reasonable error handling built-in.
