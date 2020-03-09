#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import os
import sys
import enaml
import struct
import marshal
import zipfile
from importlib.machinery import ModuleSpec

import pytest

from enaml.core.parser import parse
from enaml.core.enaml_compiler import EnamlCompiler
from enaml.core.import_hooks import MAGIC_NUMBER, make_file_info, EnamlImporter
from utils import wait_for_window_displayed, is_qt_available


pytestmark = pytest.mark.skipif(not is_qt_available(),
                                reason='Requires a Qt binding')


def generate_cache(path):
    #: Read
    with open(path, 'r') as f:
        enaml_code = f.read()

    #: Compile
    ast = parse(enaml_code, filename=path)
    code = EnamlCompiler.compile(ast, path)

    #: Generate cache
    with open('tmp.enamlc', 'wb') as f:
        f.write(MAGIC_NUMBER)
        f.write(struct.pack('i', int(os.path.getmtime(path))))
        marshal.dump(code, f)
    with open('tmp.enamlc', 'rb') as f:
        data = f.read()
    #: Cleanup
    if os.path.exists('tmp.enamlc'):
        os.remove('tmp.enamlc')

    return data


def make_library(lib):
    # Create a library.zip with the examples.

    root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..',
                            'examples', 'widgets'))

    with zipfile.ZipFile(lib, 'w') as zf:
        for src, dst in [
                         (os.path.join(root, 'buttons.enaml'),
                          'buttons.enaml'),
                         (None, 'package/__init__.py'),
                         (os.path.join(root, 'form.enaml'),
                          'package/form.enaml'),
                         (None, 'package/subpackage/__init__.py'),
                         (os.path.join(root, 'slider.enaml'),
                          'package/subpackage/slider.enaml'),
                         ]:
            if src:
                zf.write(src, dst, compress_type=zipfile.ZIP_DEFLATED)
            else:
                #: Create the __init__.py
                zf.writestr(dst, '', compress_type=zipfile.ZIP_DEFLATED)

        #: Generate cache for splitter and notebook
        for src, dst in [
                (os.path.join(root, 'splitter.enaml'),
                 make_file_info('splitter.enaml').cache_path),
                (os.path.join(root, 'notebook.enaml'),
                 make_file_info('package/subpackage/'
                                'notebook.enaml').cache_path)
                ]:
            zf.writestr(dst, generate_cache(src),
                        compress_type=zipfile.ZIP_DEFLATED)


@pytest.fixture
def zip_library():
    """ Add and remove library.zip from the sys path

    """
    lib = 'library.zip'
    # Create the zip
    make_library(lib)

    # Add to sys.path
    sys.path.append(lib)

    # Pytest handle the cleanup without the need for try finally close
    yield lib

    sys.path.remove(lib)
    #: Cleanup
    if os.path.exists(lib):
        os.remove(lib)


def assert_window_displays(enaml_qtbot, enaml_sleep, window):
    #: Make sure the imported library actually works
    window.show()
    window.send_to_front()
    wait_for_window_displayed(enaml_qtbot, window)
    enaml_qtbot.wait(enaml_sleep*1000)


def test_zipimport_from_module(enaml_qtbot, enaml_sleep, zip_library):
    with enaml.imports():
        # Test import from library.zip/buttons.enaml
        import buttons

    assert buttons.__name__ == "buttons"
    assert buttons.__file__
    assert buttons.__cached__
    assert isinstance(buttons.__loader__, EnamlImporter)
    assert isinstance(buttons.__spec__, ModuleSpec)

    assert_window_displays(enaml_qtbot, enaml_sleep, buttons.Main())


def test_zipimport_from_package(enaml_qtbot, enaml_sleep, zip_library):
    with enaml.imports():
        # Test import from library.zip/package/form.enaml
        from package import form

    assert_window_displays(enaml_qtbot, enaml_sleep, form.Main())


def test_zipimport_from_subpackage(enaml_qtbot, enaml_sleep, zip_library):
    with enaml.imports():
        # Test import from library.zip/package/subpackage/slider.enaml
        from package.subpackage import slider

    assert_window_displays(enaml_qtbot, enaml_sleep, slider.Main())


def test_zipimport_module_from_cache(enaml_qtbot, enaml_sleep, zip_library):
    with enaml.imports():
        # Test import from
        # library.zip/__enamlcache__/slider-enaml-py<ver>-cv<ver>.enamlc
        import splitter

    assert_window_displays(enaml_qtbot, enaml_sleep, splitter.Main())


def test_zipimport_package_from_cache(enaml_qtbot, enaml_sleep, zip_library):
    with enaml.imports():
        # Test import from enamlcache subpackage within zip
        # Test import from library.zip/package/subpackage/__enamlcache__/
        #                                 notebook-enaml-py<ver>-cv<ver>.enamlc
        from package.subpackage import notebook
    assert_window_displays(enaml_qtbot, enaml_sleep, notebook.Main())
