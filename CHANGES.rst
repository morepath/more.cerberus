CHANGES
=======

1.0.0 (unreleased)
------------------

- Document integrating gettext as a service with a custom TranslatorValidator.

- Add ``cerberus-stubs`` stub-only package to get Cerberus type annotations.

- Add type annotations and integrate ``mypy`` and ``pyright``.

- Switch to ``pyproject.toml`` based project setup.

- Switch to ``src-layout`` based file structure.

- Switch to native namespace package defined in PEP 420.

- Add support for Python 3.11 - 3.15.

- Drop support for Python below 3.11.

- Support Pypy 3.12.

- Switch from black, flake8, isort and pyupgrade to Ruff_ linter and formatter.

  .. _Ruff: https://docs.astral.sh/ruff

- Replace ``pre-commit`` integration with our custom tracked
  pre-commit git hook for Ruff checks on staged Python files.

- Fix linting and formatting errors.

- Update ``README.rst``.

- Remove coveralls integration.

- Update CI workflow.

- Adjust the deployment strategy:
  
  * Move the Pypi upload from ``zest.release`` to ``gh-actions``.

  * Use ``v`` + version as release tags like ``v1.0.0``.

  * So we still use ``zest.release`` but without publishing to Pypi.
    The Pypi upload is triggered by pushing the new release tag to GitHub.
    This happens in the Release workflow in ``.github/workflows/release.yml``.
    With this workflow we get Trusted Publishing with short-lived OIDC tokens
    that PyPI issues to one specific repository, workflow file and environment (``pypi``).
    We also get PEP 740 provenance and can set required reviewers for the environment
    and a ruleset who can create release tags and trigger releases.

- Make an overall cleanup.


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
