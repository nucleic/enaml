# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright (c) 2013-2018, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import os
import sys
import shutil
import pytest
import importlib
from enaml.compile_all import compileall
from utils import cd, enaml_run


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


@pytest.mark.parametrize("tutorial", [
    'employee',
    'hello_world',
    'person'
])
def test_tutorials(enaml_run, tmpdir, tutorial):
    # Run normally to generate cache files

    dir_path = os.path.abspath(os.path.split(os.path.dirname(__file__))[0])
    source = os.path.join(dir_path, 'examples', 'tutorial', tutorial)
    example = os.path.join(tmpdir.strpath, tutorial)

    # Copy to a tmp dir
    shutil.copytree(source, example)
    clean_cache(example)  # To be safe

    # Run compileall
    compileall.compile_dir(example)

    # Remove source files
    clean_source(example)

    # Add to example folder to the sys path or we get an import error
    with cd(example, add_to_sys_path=True):
        # Python only uses pyc files if copied from the pycache folder
        for f in os.listdir('__pycache__'):
            cf = ".".join(f.split(".")[:-2]) + ".pyc"
            shutil.copy(os.path.join('__pycache__', f), cf)

        # Verify it's clean
        assert not os.path.exists(tutorial+".py")
        assert not os.path.exists(tutorial+"_view.enaml")

        # Now run from cache
        mod = importlib.import_module(tutorial)
        mod.main()
