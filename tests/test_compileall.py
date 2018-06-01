# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright (c) 2013-2018, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import os
import sys
import shutil
import pytest
import importlib
from enaml.application import Application
from enaml.qt.qt_application import QtApplication
from enaml.widgets.window import Window
from enaml.compile_all import compileall
from contextlib import contextmanager
from enaml.compat import IS_PY3


@contextmanager
def cd(path):
    """ cd to the directory then return to the cwd 
    
    """
    cwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(cwd)


def clean_cache(path):
    """ Clean the cache files in the path 
    
    """
    with cd(path):
        if os.path.exists('__enamlcache__'):
            shutil.rmtree('__enamlcache__')
        if os.path.exists('__pycache__'):
            shutil.rmtree('__pycache__')
        for f in os.listdir('.'):
            if f.endswith('.pyc'):
                os.remove(f)


def clean_source(path):
    """ Clean the source files in the path 
    
    """
    with cd(path):
        for f in os.listdir('.'):
            if os.path.splitext(f)[-1] in (
                        '.py',
                        '.enaml',
                    ):
                os.remove(f)


@pytest.fixture
def enaml_run(qtbot):
    """ Patch the start method to use the qtbot """
    app = Application.instance()
    if app:
        Application._instance = None
    _start = QtApplication.start

    def start(self):
        for window in Window.windows:
            qtbot.wait_for_window_shown(window.proxy.widget)
            qtbot.wait(1000)
            window.close()
            break

    QtApplication.start = start
    try:
        yield
    finally:
        QtApplication.start = _start
        Application._instance = app


@pytest.mark.parametrize("tutorial", [
    'employee',
    'hello_world',
    'person'
])
def test_tutorials(enaml_run, tmpdir, tutorial):
    # Run normally to generate cache files
    source = os.path.join('examples', 'tutorial', tutorial)
    example = os.path.join(tmpdir.strpath, tutorial)

    # Copy to a tmp dir
    shutil.copytree(source, example)
    clean_cache(example)  # To be safe

    # Run compileall
    compileall.compile_dir(example)

    # Remove source files
    clean_source(example)

    # Add to example folder to the sys path or we get an import error
    sys.path.append(example)
    try:
        with cd(example):
            if IS_PY3:
                # PY3 only uses pyc files if copied from the pycache folder
                for f in os.listdir('__pycache__'):
                    cf = ".".join(f.split(".")[:-2]) + ".pyc"
                    shutil.copy(os.path.join('__pycache__', f), cf)

            # Verify it's clean
            assert not os.path.exists(tutorial+".py")
            assert not os.path.exists(tutorial+"_view.enaml")

            # Now run from cache
            mod = importlib.import_module(tutorial)
            mod.main()
    finally:
        sys.path.remove(example)
