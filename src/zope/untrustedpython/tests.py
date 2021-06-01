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
"""Tests for zope.security.checker
"""
import unittest
from zope.untrustedpython import interpreter, rcompile
from zope.untrustedpython.builtins import SafeBuiltins


class Test_SafeBuiltins(unittest.TestCase):

    def test_simple(self):
        d = {'__builtins__': SafeBuiltins}
        exec 'x = str(1)' in d
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
        from zope.security.interfaces import ForbiddenAttribute
        d = {}
        interpreter.exec_src("x=1", d)
        self.assertRaises(
            ForbiddenAttribute, interpreter.exec_src,
            '__builtins__.__dict__["x"] = 1', d)
        self.assertRaises(
            ForbiddenAttribute, interpreter.exec_src,
            'del __builtins__.__dict__["str"]', d)
        self.assertRaises(
            ForbiddenAttribute, interpreter.exec_src,
            '__builtins__.__dict__.update({"x": 1})', d)

    def test_no_exec(self):
        d = {}
        self.assertRaises(SyntaxError, interpreter.exec_src, "exec 'x=1'", d)

    def test_exec_code(self):
        d = {}
        code = compile('x=2', '<mycode>', 'exec')
        interpreter.exec_code(code, d)
        self.assertEqual(d['x'], 2)


class Test_Compiled(unittest.TestCase):

    def test_CompiledProgram_simple(self):
        p = interpreter.CompiledProgram('x=2')
        d = {}
        p.exec_(d)
        self.assertEqual(d['x'], 2)

    def test_CompiledProgram_output_capturing(self):
        p = interpreter.CompiledProgram('print "Hello world!"')
        import StringIO
        f = StringIO.StringIO()
        p.exec_({}, output=f)
        self.assertEqual(f.getvalue(), 'Hello world!\n')

    def test_CompiledExpression_simple(self):
        p = interpreter.CompiledExpression('x*2')
        self.assertEqual(p.eval({'x': 2}), 4)
        self.assertEqual(p.eval({}, {'x': 2}), 4)

    def test_CompiledCode_simple(self):
        code = rcompile.compile("21 * 2", "<string>", "eval")
        self.assertEqual(eval(code), 42)
        self.assertRaises(
            TypeError, rcompile.compile, object(), '<string>', 'eval')

    def test_CompiledCode_statements(self):
        exec rcompile.compile("x = 1", "<string>", "exec")
        self.assertEqual(x, 1)  # noqa: F821 undefined name 'x'

    def test_CompiledCode_no_exec(self):
        self.assertRaises(
            SyntaxError, rcompile.compile,
            "exec 'x = 2'", "<string>", "exec")
        self.assertRaises(
            SyntaxError, rcompile.compile,
            "raise KeyError('x')", "<string>", "exec")
        self.assertRaises(
            SyntaxError, rcompile.compile,
            "try: pass\nexcept: pass", "<string>", "exec")

    def test_CompiledCode_explicit_writable(self):
        import StringIO
        f = StringIO.StringIO()
        code = rcompile.compile(
            "print >> f, 'hi',\nprint >> f, 'world'", '', 'exec')
        exec code in {'f': f}
        self.assertEqual(f.getvalue(), 'hi world\n')

    def test_CompiledCode_default_output(self):
        def _exec(code, locals):
            exec code in locals
        code = rcompile.compile("print 'hi',\nprint 'world'", '', 'exec')
        self.assertRaises(NameError, _exec, code, {})
        import StringIO
        f = StringIO.StringIO()
        _exec(code, {'untrusted_output': f})
        self.assertEqual(f.getvalue(), 'hi world\n')


class Test_RestrictionMutator(unittest.TestCase):

    def test_error_no_line_info(self):
        rm = rcompile.RestrictionMutator()
        rm.error(None, 'nothing')
        self.assertEqual(rm.errors, ['nothing'])


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test_SafeBuiltins),
        unittest.makeSuite(Test_Interpreter),
        unittest.makeSuite(Test_Compiled),
        unittest.makeSuite(Test_RestrictionMutator),
    ))
