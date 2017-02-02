
from zope.untrustedpython import interpreter
from zope.untrustedpython.interpreter import compile

import pytest


def test_CompiledProgram_simple():
    p = interpreter.CompiledProgram('x=2')
    d = {}
    p.exec_(d)
    assert d['x'] == 2


def test_CompiledProgram_output_capturing():
    p = interpreter.CompiledProgram('print "Hello world!"')
    import StringIO
    f = StringIO.StringIO()
    p.exec_({}, output=f)
    assert f.getvalue() == 'Hello world!\n'


def test_CompiledExpression_simple():
    p = interpreter.CompiledExpression('x*2')
    assert p.eval({'x': 2}) == 4
    assert p.eval({}, {'x': 2}) == 4


def test_CompiledCode_simple():
    code = compile("21 * 2", "<string>", "eval")
    assert eval(code) == 42
    with pytest.raises(TypeError):
        compile(object(), '<string>', 'eval')


def test_CompiledCode_statements():
    exec compile("x = 1", "<string>", "exec")
    assert x == 1


def test_CompiledCode_no_exec():
    with pytest.raises(SyntaxError):
        compile("exec 'x = 2'", "<string>", "exec")
    with pytest.raises(SyntaxError):
        compile("raise KeyError('x')", "<string>", "exec")
    with pytest.raises(SyntaxError):
        compile("try: pass\nexcept: pass", "<string>", "exec")


def test_CompiledCode_explicit_writable():
    import StringIO
    f = StringIO.StringIO()
    code = compile("print >> f, 'hi',\nprint >> f, 'world'", '', 'exec')
    exec(code, {'f': f})
    assert f.getvalue() == 'hi world\n'


def test_CompiledCode_default_output():
    def _exec(code, locals):
        exec(code, locals)
    code = compile("print 'hi',\nprint 'world'", '', 'exec')
    with pytest.raises(NameError):
        _exec(code, {})
    import StringIO
    f = StringIO.StringIO()
    _exec(code, {'untrusted_output': f})
    assert f.getvalue() == 'hi world\n'
