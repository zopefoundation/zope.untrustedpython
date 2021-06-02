##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
from RestrictedPython import RestrictingNodeTransformer


class UntrustedPythonNodeTransformer(RestrictingNodeTransformer):
    """Custom policy which is a bit stricter than the one of RestrictedPython.

    The more strictness is needed because try/except does work properly in the
    presence of security proxies.
    """

    def visit_Raise(self, node):
        self.not_allowed(node)

    def visit_Try(self, node):
        """Deny `try`.

        This is Python 3 only, Python 2 uses TryExcept.
        """
        self.not_allowed(node)  # pragma: PY3

    def visit_TryFinally(self, node):
        """Deny `try .. finally`."""
        self.not_allowed(node)  # pragma: PY2

    def visit_ExceptHandler(self, node):
        """Deny `except`."""
        self.not_allowed(node)  # pragma: PY2

    def visit_TryExcept(self, node):
        """Deny `try ... except`.

        This is Python 2 only, Python 3 uses visit_Try*.
        """
        self.not_allowed(node)  # pragma: PY2
