import os
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
    """Test invoking the runner application.

    """
    dir_path = os.path.abspath(os.path.split(os.path.dirname(__file__))[0])
    sys.argv = ['enaml-run',
                os.path.join(dir_path,
                             'examples', 'stdlib', 'mapped_view.enaml')]
    main()
