#------------------------------------------------------------------------------
# Copyright (c) 2018, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import importlib
import os
import sys
import time
from importlib.machinery import ModuleSpec

from enaml.core.import_hooks import (AbstractEnamlImporter, EnamlImporter,
                                     imports)

import pytest


# Test handling wrong loader type
class WrongEnamlImporter(AbstractEnamlImporter):

    @classmethod
    def locate_module(cls, fullname, path=None):
        return object()

    def get_code(self):
        pass


@pytest.mark.parametrize('method', ('find_spec',))
def test_handling_wrong_locate_module_implementation(method):
    """Test handling a poorly implemented locate_module method.

    """
    loader = WrongEnamlImporter()
    with pytest.raises(ImportError):
        getattr(loader, method)('module_name')


SOURCE =\
"""
from enaml.widgets.api import *

enamldef Main(Window):

    Field: fd:
        name = 'content'

"""


@pytest.yield_fixture()
def enaml_module(tmpdir):
    """Create an enaml module in a tempdir and add it to sys.path.

    """
    name = '__enaml_test_module__'
    folder = str(tmpdir)
    path = os.path.join(folder, name + '.enaml')
    with open(path, 'w') as f:
        f.write(SOURCE)
    sys.path.append(folder)

    yield name, folder, path

    sys.path.remove(folder)
    if name in sys.modules:
        del sys.modules[name]


def test_import_and_cache_generation(enaml_module):
    """Test importing a module and checking that the cache was generated.

    """
    name, folder, _ = enaml_module
    with imports():
        importlib.import_module(name)

    assert name in sys.modules

    # Check that the module attributes are properly populated
    mod = sys.modules[name]
    assert mod.__name__ == name
    assert mod.__file__ == os.path.join(folder, name + ".enaml")
    assert os.path.join(folder, "__enamlcache__") in mod.__cached__
    assert isinstance(mod.__loader__, EnamlImporter)
    assert isinstance(mod.__spec__, ModuleSpec)

    cache_folder = os.path.join(folder, '__enamlcache__')
    assert os.path.isdir(cache_folder)
    cache_name = os.listdir(cache_folder)[0]
    assert name in cache_name
    assert '.enamlc' in cache_name


def test_import_when_cache_exists(enaml_module):
    """Test importing a module when the cache exists.

    """
    name, folder, _ = enaml_module
    assert name not in sys.modules
    with imports():
        importlib.import_module(name)

    assert name in sys.modules
    del sys.modules[name]

    cache_folder = os.path.join(folder, '__enamlcache__')
    assert os.path.isdir(cache_folder)
    cache_name = os.listdir(cache_folder)[0]
    cache_path = os.path.join(cache_folder, cache_name)
    cache_time = os.path.getmtime(cache_path)

    with imports():
        importlib.import_module(name)

    assert os.path.getmtime(cache_path) == cache_time
    assert name in sys.modules


def test_import_cache_only(enaml_module):
    """Test importing a module for which we have no sources.

    """
    name, _, path = enaml_module
    with imports():
        importlib.import_module(name)

    assert name in sys.modules
    del sys.modules[name]
    os.remove(path)

    with imports():
        importlib.import_module(name)

    assert name in sys.modules


def test_handling_importing_a_bugged_module(enaml_module):
    """Test that when importing a bugged module it does not stay in sys.modules

    """
    name, _, path = enaml_module
    with open(path, 'a') as f:
        f.write('\nraise RuntimeError()')

    with imports():
        with pytest.raises(RuntimeError):
            importlib.import_module(name)

    assert name not in sys.modules


@pytest.yield_fixture
def enaml_importer():
    """Standard enaml importer whose state is restored after testing.

    """
    print(imports, dir(imports))
    old = imports.get_importers()

    yield imports

    imports._imports__importers = old


def test_importer_management(enaml_importer):
    """Test managing manually enaml importers.

    """
    standard_importers_numbers = len(enaml_importer.get_importers())
    enaml_importer.add_importer(WrongEnamlImporter)
    assert WrongEnamlImporter in enaml_importer.get_importers()
    enaml_importer.add_importer(WrongEnamlImporter)
    assert (len(enaml_importer.get_importers()) ==
            standard_importers_numbers + 1)
    enaml_importer.remove_importer(WrongEnamlImporter)

    # Test removing twice
    enaml_importer.remove_importer(WrongEnamlImporter)

    with pytest.raises(TypeError):
        enaml_importer.add_importer(object)
