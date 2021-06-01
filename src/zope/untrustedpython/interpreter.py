##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Restricted interpreter.

TODO: This code needs a serious security review!!!
"""
from zope.untrustedpython.builtins import SafeBuiltins
from zope.untrustedpython.rcompile import compile


def exec_code(code, globals, locals=None):
    globals['__builtins__'] = SafeBuiltins
    exec code in globals, locals


def exec_src(source, globals, locals=None):
    globals['__builtins__'] = SafeBuiltins
    code = compile(source, '<string>', 'exec')
    exec code in globals, locals


class CompiledExpression(object):
    """A compiled expression
    """

    def __init__(self, source, filename='<string>'):
        self.source = source
        self.code = compile(source, filename, 'eval')

    def eval(self, globals, locals=None):
        globals['__builtins__'] = SafeBuiltins
        if locals is None:
            return eval(self.code, globals)
        else:
            return eval(self.code, globals, locals)


class CompiledProgram(object):
    """A compiled expression
    """

    def __init__(self, source, filename='<string>'):
        self.source = source
        self.code = compile(source, filename, 'exec')

    def exec_(self, globals, locals=None, output=None):
        globals['__builtins__'] = SafeBuiltins
        if output is not None:
            globals['untrusted_output'] = output
        exec self.code in globals, locals
