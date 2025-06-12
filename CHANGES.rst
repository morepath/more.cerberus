CHANGES
=======

0.4 (2025-06-12)
----------------

- Add support for custom error messages with placeholders
  {constraint}, {field} and {value}. When ``error.info`` tuple
  is available, you can also use positional placeholders ({0}, {1})
  in the error messages.

- Add translation support for error messages.

- Drop support for Python 3.4 - 3.7.

- Add support for Python 3.9 - 3.12.

- Use GitHub Actions for CI.


0.3 (2020-04-26)
----------------

- **Removed**: Removed support for Python 2.
  
  You have to upgrade to Python 3 if you want to use this version.

- Added support for Python 3.7 and 3.8 and PyPy 3.6.

- Make Python 3.7 the default testing environment.

- Upgrade Cerberus to version 1.3.2.

- Add integration for the Black code formatter.


0.2 (2018-02-11)
----------------

- Add Python 3.6 support.
- Add example for creating a custom error view to README.
- Some smaller fixes.


0.1 (2017-03-17)
----------------

- initial public release.
