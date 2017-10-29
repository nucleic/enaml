#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from future.builtins import int
from atom.api import Validate, Value


class StrengthMember(Value):
    """ A custom Atom member class that validates a strength.

    The strength can be None, a number, or one of the strength strings:
    'weak', 'medium', 'strong', or 'required'.

    """
    __slots__ = ()

    def __init__(self, default=None, factory=None):
        super(StrengthMember, self).__init__(default, factory)
        self.set_validate_mode(Validate.MemberMethod_ObjectOldNew, 'validate')

    def validate(self, owner, old, new):
        if new is not None:
            if not isinstance(new, (float, int)):
                if new not in ('weak', 'medium', 'strong', 'required'):
                    msg = "A strength must be a number or 'weak', 'medium' "
                    msg += "'strong', or 'required'. Got %r instead." % new
                    raise TypeError(msg)
        return new
