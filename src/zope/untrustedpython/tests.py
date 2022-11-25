##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import unittest

import six

from zope.untrustedpython import interpreter
from zope.untrustedpython import rcompile
from zope.untrustedpython.builtins import SafeBuiltins


if six.PY2:
    from StringIO import StringIO  # pragma: PY2
else:
    from io import StringIO  # pragma: PY3


class Test_SafeBuiltins(unittest.TestCase):

    def test_simple(self):
        d = {'__builtins__': SafeBuiltins}
        exec('x = str(1)', d)
        self.assertEqual(d['x'], '1')

    def test_immutable(self):
        self.assertRaises(
            AttributeError, setattr, SafeBuiltins, 'foo', 1)
        self.assertRaises(
            AttributeError, delattr, SafeBuiltins, 'foo')

    def test_no_unsafe_objects(self):
        self.assertRaises(
            AttributeError, getattr, SafeBuiltins, 'eval')
        self.assertRaises(
            AttributeError, getattr, SafeBuiltins, 'globals')

    def test_import(self):
        imp = SafeBuiltins.__import__
        import zope.security
        self.assertEqual(imp('zope.security'), zope)
        self.assertEqual(imp('zope.security', {}, {}, ['*']), zope.security)
        self.assertEqual(type(imp('zope.security')), zope.security.proxy.Proxy)

    def test_no_new_import(self):
        imp = SafeBuiltins.__import__
        import zope.security
        security = zope.security
        import sys
        del sys.modules['zope.security']
        self.assertRaises(ImportError, imp, 'zope.security')
        sys.modules['zope.security'] = security

    def test_relative_import(self):
        imp = SafeBuiltins.__import__
        import zope.security
        self.assertEqual(
            imp('security', {'__name__': 'zope', '__path__': []}),
            zope.security)
        self.assertEqual(
            imp('security', {'__name__': 'zope.foo'}),
            zope.security)


class Test_Interpreter(unittest.TestCase):

    def test_simple(self):
        d = {}
        interpreter.exec_src("x=1", d)
        self.assertEqual(d['x'], 1)
        self.assertEqual(d['__builtins__'], SafeBuiltins)

    def test_proxied(self):
        d = {}
        interpreter.exec_src('str=str', d)
        from zope.security.proxy import Proxy
        self.assertEqual(type(d['str']), Proxy)

    def test_no_builtins_mutations(self):
        d = {}
        interpreter.exec_src("x=1", d)
        with self.assertRaises(SyntaxError) as err:
            interpreter.exec_src('__builtins__.__dict__["x"] = 1', d)
        self.assertIn('"__dict__" is an invalid attribute name',
                      str(err.exception))
        with self.assertRaises(SyntaxError) as err:
            interpreter.exec_src('del __builtins__.__dict__["str"]', d)
        self.assertIn('"__builtins__" is an invalid variable',
                      str(err.exception))
        with self.assertRaises(SyntaxError) as err:
            interpreter.exec_src('__builtins__.__dict__.update({"x": 1})', d)
        self.assertIn('"__builtins__" is an invalid variable',
                      str(err.exception))

    def test_no_exec(self):
        with self.assertRaises(SyntaxError) as err:
            interpreter.exec_src("exec('x=1')", {})
        if six.PY2:
            self.assertEqual("('Line 1: Exec statements are not allowed.',)",
                             str(err.exception))  # pragma: PY2
        else:
            self.assertEqual("('Line 1: Exec calls are not allowed.',)",
                             str(err.exception))  # pragma: PY3

    def test_exec_code(self):
        d = {}
        code = rcompile.compile('x=2', '<mycode>', 'exec')
        interpreter.exec_code(code, d)
        self.assertEqual(d['x'], 2)


class Test_Compiled(unittest.TestCase):

    def test_CompiledProgram_simple(self):
        p = interpreter.CompiledProgram('x=2')
        d = {}
        p.exec_(d)
        self.assertEqual(d['x'], 2)

    def test_CompiledProgram_output_capturing(self):
        # assignment to `res` is done to prevent a warning about not reading
        # `printed` variable
        p = interpreter.CompiledProgram('print("Hello world!"); res=printed')
        globals = {}
        f = StringIO()
        p.exec_(globals, output=f)
        self.assertEqual(f.getvalue(), 'Hello world!\n')

    def test_CompiledExpression_simple(self):
        p = interpreter.CompiledExpression('x * 2')
        self.assertEqual(p.eval({'x': 2}), 4)
        self.assertEqual(p.eval({}, {'x': 2}), 4)

    def test_CompiledExpression_getattr(self):
        p = interpreter.CompiledExpression('x.real')
        self.assertEqual(p.eval({'x': 3 + 2j}), 3.0)
        self.assertEqual(p.eval({}, {'x': 4 + 3j}), 4.0)

    def test_CompiledCode_simple(self):
        code = rcompile.compile("21 * 2", "<string>", "eval")
        self.assertEqual(eval(code), 42)

    def test_compile_invalid_code_type(self):
        with self.assertRaises(TypeError):
            rcompile.compile(object(), '<string>', 'eval')

    def test_CompiledCode_statements(self):
        exec(rcompile.compile("x = 1", "<string>", "exec"), globals())
        # `exec` put `x` into the globals:
        self.assertEqual(x, 1)  # noqa: F821 undefined name 'x'

    def test_CompiledCode_no_exec(self):
        with self.assertRaises(SyntaxError) as err:
            rcompile.compile("exec('x = 2')", "<string>", "exec")
        if six.PY2:
            self.assertEqual("('Line 1: Exec statements are not allowed.',)",
                             str(err.exception))  # pragma: PY2
        else:
            self.assertEqual("('Line 1: Exec calls are not allowed.',)",
                             str(err.exception))  # pragma: PY3
        with self.assertRaises(SyntaxError) as err:
            rcompile.compile("raise KeyError('x')", "<string>", "exec")
        self.assertEqual("('Line 1: Raise statements are not allowed.',)",
                         str(err.exception))
        with self.assertRaises(SyntaxError) as err:
            rcompile.compile("try: pass\nexcept: pass", "<string>", "exec")
        if six.PY2:
            self.assertEqual(
                "('Line 1: TryExcept statements are not allowed.',)",
                str(err.exception))  # pragma: PY2
        else:
            self.assertEqual(
                "('Line 1: Try statements are not allowed.',)",
                str(err.exception))  # pragma: PY3
