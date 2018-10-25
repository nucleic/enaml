import sys
import pytest
from utils import enaml_run

from enaml.application import Application, deferred_call
from enaml.runner import main


@pytest.fixture
def sys_argv():
    """ Fixture that saves sys.argv and restores it after the test completes 
    
    """
    argv = sys.argv
    try:
        yield
    finally:
        sys.argv = argv


def test_runner(enaml_run, sys_argv):
    sys.argv = ['enaml-run', 'examples/stdlib/mapped_view.enaml']
    main()
    
