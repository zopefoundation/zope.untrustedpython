=======
CHANGES
=======

5.0 (unreleased)
------------------

Backwards incompatible changes
++++++++++++++++++++++++++++++

- Require ``RestrictedPython >= 4``.

- Drop support for writing output of ``print`` calls to a variable named
  ``untrusted_output``. It is now done the same way ``RestrictedPython``
  handles printing, i. e. access it trough the variable ``printed``.
  ``.interpreter.CompiledProgram`` still supports output to a file like object
  by implementing accessing the printed data.

- Drop support for Python 2.6.

4.0.0 (2013-02-12)
------------------

- Test coverage at 100%.

- Package extracted from zope.security, preserving revision history
