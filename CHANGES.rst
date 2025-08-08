=======
CHANGES
=======

7.0 (unreleased)
----------------

- Replace ``pkg_resources`` namespace with PEP 420 native namespace.


6.2 (2025-08-08)
----------------

- Add support for Python 3.12, 3.13.

- Drop support for Python 3.7, 3.8.


6.1 (2024-08-02)
----------------

- Update safe builtins for Python 3, adding ``bytes``, and removing ``cmp``,
  ``coerce``, ``long``, ``reduce``, ``unichr``, and ``unicode``.


6.0 (2023-09-13)
----------------

- Drop support for Python 2.7, 3.5, 3.6.

- Make sure the tests do not fail even on unsupported PyPy3 because ZTK might
  run them.


5.0 (2022-11-29)
----------------

Backwards incompatible changes
++++++++++++++++++++++++++++++

- Require ``RestrictedPython >= 4``.

- Drop support for writing output of ``print`` calls to a variable named
  ``untrusted_output``. It is now done the same way ``RestrictedPython``
  handles printing, i. e. access it trough the variable ``printed``.
  ``.interpreter.CompiledProgram`` still supports output to a file like object
  by implementing accessing the printed data.

- The following names are no longer available via ``__builtins__`` as they are
  either potentially harmful, not accessible at all or meaningless:

    + ``__debug__``
    + ``__name__``
    + ``__doc__``
    + ``copyright``
    + ``credits``
    + ``license``
    + ``quit``

- Drop support to run the tests using ``python setup.py test``.

- Drop support for Python 2.6.

Features
++++++++

- Add support for Python 3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 3.11.


4.0.0 (2013-02-12)
------------------

- Test coverage at 100%.

- Package extracted from zope.security, preserving revision history
