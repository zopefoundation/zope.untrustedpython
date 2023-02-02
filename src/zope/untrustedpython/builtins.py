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
"""Protection of built-in objects.
"""
from types import ModuleType

from zope.security.checker import NamesChecker
from zope.security.proxy import ProxyFactory


def SafeBuiltins():

    safe_builtins = {}

    import builtins

    _builtinTypeChecker = NamesChecker(
        ['__str__', '__repr__', '__name__', '__module__',
         '__bases__', '__call__'])

    # It's better to say what is safe than it say what is not safe
    safe_names = [
        # Names of safe objects. See untrustedinterpreter.txt for a
        # definition of safe objects.

        'ArithmeticError', 'AssertionError', 'AttributeError',
        'DeprecationWarning', 'EOFError', 'Ellipsis', 'EnvironmentError',
        'Exception', 'FloatingPointError', 'IOError', 'ImportError',
        'IndentationError', 'IndexError', 'KeyError', 'KeyboardInterrupt',
        'LookupError', 'MemoryError', 'NameError', 'None', 'NotImplemented',
        'NotImplementedError', 'OSError', 'OverflowError', 'OverflowWarning',
        'ReferenceError', 'RuntimeError', 'RuntimeWarning', 'StandardError',
        'StopIteration', 'SyntaxError', 'SyntaxWarning', 'SystemError',
        'SystemExit', 'TabError', 'TypeError', 'UnboundLocalError',
        'UnicodeError', 'UserWarning', 'ValueError', 'Warning',
        'ZeroDivisionError',
        'abs', 'bool',
        'callable', 'chr', 'classmethod', 'cmp', 'coerce',
        'complex', 'delattr',
        'dict', 'divmod', 'filter', 'float', 'frozenset', 'getattr',
        'hasattr', 'hash', 'hex', 'id', 'int', 'isinstance',
        'issubclass', 'iter', 'len', 'list',
        'long', 'map', 'max', 'min', 'object', 'oct', 'ord', 'pow',
        'property', 'range', 'reduce', 'repr', 'reversed', 'round',
        'set', 'setattr', 'slice', 'sorted', 'staticmethod', 'str', 'super',
        'tuple', 'type', 'unichr', 'unicode', 'vars', 'zip',
        'True', 'False',

        # TODO: dir segfaults with a seg fault due to a bad tuple
        # check in merge_class_dict in object.c. The assert macro
        # seems to be doing the wrong think. Basically, if an object
        # has bases, then bases is assumed to be a tuple.
        # dir,
    ]

    for name in safe_names:
        try:
            value = getattr(builtins, name)
        except AttributeError:
            pass
        else:
            if isinstance(value, type):
                value = ProxyFactory(value, _builtinTypeChecker)
            else:
                value = ProxyFactory(value)
            safe_builtins[name] = value

    from sys import modules

    def _imp(name, fromlist, prefix=''):
        module = modules.get(prefix + name)
        if module is not None:
            if fromlist or ('.' not in name):
                return module
            return modules[prefix + name.split('.')[0]]

    def __import__(name, globals=None, locals=None, fromlist=()):
        # Waaa, we have to emulate __import__'s weird semantics.

        if globals:
            __name__ = globals.get('__name__')
            if __name__:
                # Maybe do a relative import
                if '__path__' not in globals:
                    # We have an ordinary module, not a package,
                    # so remove last name segment:
                    __name__ = '.'.join(__name__.split('.')[:-1])
                if __name__:
                    module = _imp(name, fromlist, __name__ + '.')
                    if module is not None:
                        return module

        module = _imp(name, fromlist)
        if module is not None:
            return module

        raise ImportError(name)

    safe_builtins['__import__'] = ProxyFactory(__import__)

    return safe_builtins


class ImmutableModule(ModuleType):
    def __init__(self, name='__builtins__', **kw):
        ModuleType.__init__(self, name)
        self.__dict__.update(kw)

    def __setattr__(self, name, v):
        raise AttributeError(name)

    def __delattr__(self, name):
        raise AttributeError(name)


SafeBuiltins = ImmutableModule(**SafeBuiltins())
