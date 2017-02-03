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
"""
"""

from RestrictedPython import RestrictingNodeTransformer

import ast


class UntrustedPythonNodeTransformer(RestrictingNodeTransformer):

    def visit_Getattr(self, node):
        """Converts attribute access to a function call.

        'foo.bar' becomes 'getattr(foo, "bar")'.

        Also prevents augmented assignment of attributes, which would
        be difficult to support correctly.
        """
        # TODO: Implement
        # return ast.CallFunc(_getattr_name,
        #                    [node.expr, ast.Const(node.attrname)])

    def visit_Print(self, node):
        """Make sure prints always have a destination

        If we get a print without a destination, make the default destination
        untrusted_output.
        """
        # TODO: Implement it save, based on PrintCollector
        if node.dest is None:
            node.dest = ast.Name('untrusted_output',
                                 ast.Load(),
                                 lineno=node.lineno)
        return self.node_contents_visit(node)

    # TODO: Implement equivalent for print function

    def visit_Exec(self, node):
        self.not_allowed(node)

    def visit_Raise(self, node):
        self.not_allowed(node)

    def visit_TryExcept(self, node):
        self.not_allowed(node)
