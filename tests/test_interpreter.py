
from zope.untrustedpython import interpreter
from zope.untrustedpython.builtins import SafeBuiltins
from zope.untrustedpython.interpreter import compile

import pytest


def test_simple():
    d = {}
    interpreter.exec_src("x=1", d)
    assert d['x'] == 1
    assert d['__builtins__'] == SafeBuiltins


def test_proxied():
    d = {}
    interpreter.exec_src('str=str', d)
    from zope.security.proxy import Proxy
    assert type(d['str']), Proxy


def test_no_builtins_mutations():
    from zope.security.interfaces import ForbiddenAttribute
    d = {}
    interpreter.exec_src("x=1", d)
    with pytest.raises(ForbiddenAttribute):
        interpreter.exec_src('__builtins__.__dict__["x"] = 1', d)
    with pytest.raises(ForbiddenAttribute):
        interpreter.exec_src('del __builtins__.__dict__["str"]', d)
    with pytest.raises(ForbiddenAttribute):
        interpreter.exec_src('__builtins__.__dict__.update({"x": 1})', d)


def test_no_exec():
    d = {}
    with pytest.raises(SyntaxError):
        interpreter.exec_src("exec 'x=1'", d)


def test_exec_code():
    d = {}
    code = compile('x=2', '<mycode>', 'exec')
    interpreter.exec_code(code, d)
    assert d['x'], 2
