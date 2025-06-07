more.cerberus: validation and normalization support for Morepath
================================================================

This package provides Morepath integration for the Cerberus_ data validation
library:

.. _Cerberus: http://python-cerberus.org

Cerberus can automate user input validation and normalization in a HTTP API.
We also support custom error messages and translations for multi-language
applications.


Schema
------

You can define a schema simply as a Python dict:

.. code-block:: python

  user_schema = {
    'name': {'type': 'string', 'minlength' : 3, 'required': True},
    'age': {'type': 'integer', 'min': 0, 'required': True}
  }

Alternatively you can define the schema in yaml and load it
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
      def _check_with_validate_email(self, field, value):
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
    'name': {
      'type': 'string',
      'minlength' : 3,
      'required': True,
    },
    'email': {
      'type': 'string',
      'check_with': 'validate_email',
      'coerce': 'normalize_email',
      'required': True,
    }
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
      check_with: validate_email
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
      def _check_with_verify_email(self, field, value):
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


Custom Error Messages and Translation
-------------------------------------

You can customize error messages and translate them using Cerberus
integration in more.cerberus. This is useful for multi-language applications
and for providing more user-friendly validation errors.

Basic Usage
~~~~~~~~~~~

You can customize error messages with placeholders:

.. code-block:: python

  from more.cerberus import loader

  # Define your schema
  schema = {
      "name": {"type": "string", "minlength": 3, "required": True},
      "age": {"type": "integer", "min": 18, "required": True},
  }

  # Define custom messages
  messages = {
      "required": "This field is mandatory",
      "minlength": "Must be at least {minlength} characters",
      "min": "Must be at least {min}"
  }

  # Create your validator without translation
  validator = loader(schema, message_mapping=messages)

  # With a translation function using Python's standard gettext
  import gettext
  translations = gettext.translation('myapp', 'locale', languages=['de'])
  _ = translations.gettext
  validator_i18n = loader(schema, translator_func=_, message_mapping=messages)

Always use curly braces {} for placeholders in your custom error messages.
Supported placeholders include:

- ``{constraint}``: The general validation constraint value
                    (compatible with all rules)
- Rule-specific placeholders matching the rule names:

  - ``{min}``: For min value validation
  - ``{max}``: For max value validation
  - ``{minlength}``: For minimum string length
  - ``{maxlength}``: For maximum string length
  - ``{type}``: For type validation (also handles complex types like "string or integer")

- ``{field}``: The field name being validated
- ``{value}``: The value that failed validation

Placeholders will be automatically replaced with their actual values
during validation. You can use either ``{constraint}`` or rule-specific
placeholders in your message templates.

Translation Integration
~~~~~~~~~~~~~~~~~~~~~~~

The translation functionality is designed to work with any gettext-based
translation system:

- Python's built-in gettext module
- Babel-based translation systems
- Any custom translation function that takes a string and returns a
  translated string

You can also specify a translation domain when initializing the loader:

.. code-block:: python

  # Specify a custom translation domain (default is "messages")
  translations = gettext.translation('my_domain', 'locale', languages=['de'])
  _ = translations.gettext
  validator = loader(schema, translator_func=_)

The ``translation_domain`` parameter helps organize translations into
separate catalogs in gettext-based translation systems. This allows
you to keep validation error messages in their own namespace,
separate from other application translations.

Message Mapping
~~~~~~~~~~~~~~~

You can define custom messages for any Cerberus validation rule.
Use the same rule names as in your schema:

- ``required``: For required fields
- ``minlength``: For string minimum length (with ``{minlength}`` placeholder)
- ``maxlength``: For string maximum length (with ``{maxlength}`` placeholder)
- ``type``: For type validation errors (with ``{type}``  or ``{constraint}`` placeholder)
- ``min``: For minimum numeric values (with ``{min}`` or ``{constraint}`` placeholder)
- ``max``: For maximum numeric values (with ``{max}`` or ``{constraint}`` placeholder)
- ``regex``: For regular expression validation errors
- ... and others from Cerberus

You can use either specific rule name placeholders (like ``{min}``)
or the general ``{constraint}`` placeholder which is part of Cerberus'
built-in error system.

Here's how placeholders are substituted at runtime:

.. code-block:: python

  # Schema definition
  schema = {"age": {"type": "integer", "min": 18}}
  message_mapping = {"min": "Value must be at least {min}"}
  # or using constraint: message_mapping = {"min": "Value must be at least {constraint}"}

  # What users will see when they enter "10" as age:
  # "Value must be at least 18"

Multiple Type Validation
~~~~~~~~~~~~~~~~~~~~~~~~

The library handles complex type validations elegantly.
For example, when a field can accept multiple types:

.. code-block:: python

  # Schema accepting either string or integer
  schema = {"id": {"type": ["string", "integer"]}}
  message_mapping = {"type": "Must be either {type}"}

  # What users will see with invalid input:
  # "Must be either string or integer"

YAML Message Mapping
~~~~~~~~~~~~~~~~~~~~

You can also organize message mappings hierarchically using YAML files.
For example:

.. code-block:: yaml

  # messages.yml
  required: This field is mandatory
  min: Value must be at least {min}
  max: Value must not exceed {max}
  type: Field must be of {type} type
  minlength: Must be at least {minlength} characters
  maxlength: Cannot exceed {maxlength} characters
  regex: Invalid format

Then load them in your Python code:

.. code-block:: python

  import yaml

  with open('messages.yml') as f:
      message_mapping = yaml.safe_load(f)

  validator = loader(schema, message_mapping=message_mapping)

- Define global default messages in a central location
  (e.g., ``settings/default_messages.yml``)
- Override specific messages with module-level files
  (e.g., ``users/messages.yml``)
- Load and merge these mappings before passing them to the validator

Translation Extraction
~~~~~~~~~~~~~~~~~~~~~~

When using YAML files for message definitions, you'll need a way to extract
those strings for translation. A recommended approach is to create a script
that reads all your YAML message files and generates a Python file with the
messages wrapped in translation markers.

Here's a simple example of such a script:

.. code-block:: python

  #!/usr/bin/env python
  import yaml
  import sys
  from pathlib import Path

  # Find message files in your project
  source_dir = Path("src")
  yaml_files = list(source_dir.glob("**/*messages.yml"))

  # Write header to output file
  output_file = open("translations/validation_messages.py", "w")
  print("# Generated translation markers", file=output_file)
  print("def _(text): return text\n", file=output_file)

  # Process each YAML file
  for yaml_file in yaml_files:
      print(f"# From {yaml_file}:", file=output_file)
      with open(yaml_file) as f:
          messages = yaml.safe_load(f) or {}

      # Extract messages for translation
      for key, message in messages.items():
          if message and isinstance(message, str):
              print(f'_("{message}")  # {key}', file=output_file)

This generated file can then be processed with standard translation tools like
Babel/pybabel to create .po files, which you would then translate and compile
into .mo files following your regular translation workflow.

Example in a Morepath App
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

  import gettext
  from more.cerberus import CerberusApp, loader
  from morepath import redirect

  class App(CerberusApp):
      pass

  user_schema = {
      "name": {"type": "string", "required": True},
      "email": {"type": "string", "required": True}
  }

  messages = {
      "required": "This field is required.",
      "type": "Must be of {constraint} type"
  }

  # Set up translations for the view
  translations = gettext.translation('messages', 'locale', languages=['de'])
  _ = translations.gettext

  @App.json(
    model=User,
    request_method="POST",
    load=loader(user_schema, translator_func=_, message_mapping=messages)
  )
  def create_user(self, request, json):
      # Handle validated input


Troubleshooting
---------------

Here are solutions to common issues you might encounter:

Missing Placeholders
~~~~~~~~~~~~~~~~~~~~

If placeholders in your error messages aren't being replaced:

1. Verify that you're using the correct placeholder syntax: ``{constraint}``,
   ``{value}`` and ``{field}``.
2. Check that the rule name in your message_mapping matches the rule
   in your schema

Translation Issues
~~~~~~~~~~~~~~~~~~

If translations aren't working as expected:

1. Make sure your translator function is callable and returns a string
2. Verify your .po/.mo files are properly formatted and located
3. Test your translator function independently to confirm it works
4. Remember that placeholders are replaced before translation occurs

Complex Validation Rules
~~~~~~~~~~~~~~~~~~~~~~~~

For complex validations with custom rules:

1. Define custom error messages that include ``{constraint}`` placeholders
2. Use the ``{field}`` placeholder to indicate which field failed validation
3. Consider using the ``{value}`` placeholder to show the invalid input
   in error messages

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

If you want a different error view you can instead create it
by yourself, e.g.:

.. code-block:: python

  from more.cerberus.error import ValidationError

  from .app import App


  @App.json(model=ValidationError)
  def validation_error(self, request):
      @request.after
      def set_status(response):
          response.status = 422

      errors = list(self.errors.values())[0][0]

      return {
          'errors': errors
      }

This could be used to extract the errors from a schema wrapped into
a dictionary like:

.. code-block:: yaml

  article-schema:
    article:
      type: dict
      schema:
        title:
          type: string
          required: true
        body:
          type: string
          required: true
