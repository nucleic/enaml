#------------------------------------------------------------------------------
#  Copyright (c) 2013, Nucleic Development Team
#  All rights reserved.
#------------------------------------------------------------------------------
from atom.api import Atom, Float


class Myclass(Atom):
    """ This is a example class

    It is used to demonstrate the proposed guidelines for documenting atom
    based classes in an "sphinx-friendly" way.

    The atoms are documented close to their definition by using a special
    comment ``#:`` prefix.

    """

    #: The x Float atom (default = 150.0)
    x = Float(150.0)

    # This is a comment autodoc ignores it
    #: The y Float atom (default = 0.0)
    y = Float(0.0)


class Otherclass(Atom):
    """ This is another example class using atom

    It is used to demonstrate the alternative method for documenting atom
    based classes in an "sphinx-friendly" way.

    The atoms are documented at the start of the class definition.

    Attributes
    ----------
    x : Float, default = 150.0
        The x Float atom

    y : Float, default = 150.0
        The y Float atom

    """

    x = Float(150.0)

    # This is a comment autodoc ignores it
    y = Float(0.0)
