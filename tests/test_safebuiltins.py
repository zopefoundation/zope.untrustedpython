
from zope.untrustedpython.builtins import SafeBuiltins

import pytest


def test_simple():
    d = {'__builtins__': SafeBuiltins}
    exec('x = str(1)', d)
    assert d['x'] == '1'


def test_immutable():
    with pytest.raises(AttributeError):
        setattr(SafeBuiltins, 'foo', 1)
    with pytest.raises(AttributeError):
        delattr(SafeBuiltins, 'foo')


def test_no_unsafe_objects():
    with pytest.raises(AttributeError):
        getattr(SafeBuiltins, 'eval')
    with pytest.raises(AttributeError):
        getattr(SafeBuiltins, 'globals')


def test_import():
    imp = SafeBuiltins.__import__
    import zope.security
    assert imp('zope.security') == zope
    assert imp('zope.security', {}, {}, ['*']) == zope.security
    assert type(imp('zope.security')) == zope.security.proxy.Proxy


def test_no_new_import():
    imp = SafeBuiltins.__import__
    import zope.security
    security = zope.security
    import sys
    del sys.modules['zope.security']
    with pytest.raises(ImportError):
        imp('zope.security')
    sys.modules['zope.security'] = security

def test_relative_import():
    imp = SafeBuiltins.__import__
    import zope.security
    assert imp('security', {'__name__': 'zope', '__path__': []}) == zope.security
    assert imp('security', {'__name__': 'zope.foo'}) == zope.security
