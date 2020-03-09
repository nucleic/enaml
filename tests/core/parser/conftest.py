#------------------------------------------------------------------------------
# Copyright (c) 2018, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#-----------------------------------------------------------------------------
import pytest
from enaml.core.parser import write_tables


@pytest.fixture(scope='session', autouse=True)
def update_parser():
    """Force update of the parser when running the test.

    """
    write_tables()
