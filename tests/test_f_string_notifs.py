#------------------------------------------------------------------------------
# Copyright (c) 2018, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
"""Test the handling of nested functions such as lambda functions and
implicit functions used by comprehensions.

"""
import sys

import pytest

from utils import compile_source

SYNCHRONISATION_TEMPLATE =\
"""from enaml.widgets.api import Window, Container, Field, Label

enamldef Main(Window):

    attr colors = ['red', 'blue', 'yellow', 'green']
    alias search_txt : search.text
    alias formatted_comp : lab.text

    Container: container:

        Field: search:
            placeholder = "Search..."
        Label: lab:
            text << f'{colors}'

"""

@pytest.mark.skipif(sys.version_info < (3, 6), reason='Requires Python 3.6')
def test_tracing_fstring():
    """Test that an f-string can be traced.

    """
    source = SYNCHRONISATION_TEMPLATE
    win = compile_source(source, 'Main')()
    assert win.formatted_comp == "['red', 'blue', 'yellow', 'green']"
    win.colors = ['yellow', 'red', 'blue', 'green']
    assert win.formatted_comp == "['yellow', 'red', 'blue', 'green']"