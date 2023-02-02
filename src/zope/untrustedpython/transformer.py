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
        """Deny `raise`."""
        self.not_allowed(node)

    def visit_Try(self, node):
        """Deny `try`."""
        self.not_allowed(node)
