#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import os
import sys
import enaml
import struct
import marshal
import zipfile
from io import BytesIO
from enaml.core.parser import parse
from enaml.core.enaml_compiler import EnamlCompiler
from enaml.core.import_hooks import MAGIC, make_file_info
from utils import wait_for_window_displayed, compile_source


def generate_cache(path):
    #: Read
    with open(path, 'rU') as f:
        enaml_code = f.read()

    #: Compile
    ast = parse(enaml_code, filename=path)
    code = EnamlCompiler.compile(ast, path)

    #: Generate cache
    data = BytesIO()
    data.write(MAGIC)
    data.write(struct.pack('i', int(os.path.getmtime(path))))
    marshal.dump(code, data)
    return data.getvalue()


def make_library(lib):
    # Create a library.zip with the examples.

    with zipfile.ZipFile(lib, 'w') as zf:
        for src, dst in [
                          ('examples/widgets/buttons.enaml', 'buttons.enaml'),
                          (None, 'package/__init__.py'),
                          ('examples/widgets/form.enaml', 'package/form.enaml'),
                          (None, 'package/subpackage/__init__.py'),
                          ('examples/widgets/slider.enaml', 'package/subpackage/slider.enaml'),

                         ]:
            if src:
                zf.write(src, dst, compress_type=zipfile.ZIP_DEFLATED)
            else:
                #: Create the __init__.py
                zf.writestr(dst, '', compress_type=zipfile.ZIP_DEFLATED)

        #: Generate cache for splitter and notebook
        for src, dst in [
                ('examples/widgets/splitter.enaml',
                    make_file_info('splitter.enaml').cache_path),
                ('examples/widgets/notebook.enaml',
                    make_file_info('package/subpackage/notebook.enaml').cache_path)
            ]:
            zf.writestr(dst, generate_cache(src), compress_type=zipfile.ZIP_DEFLATED)


def with_library(f):
    #: Add and remove library.zip from the sys path
    def test_with_library(enaml_qtbot, enaml_sleep, *args,**kwargs):
        lib = 'library.zip'
        #: Create the zip
        make_library(lib)

        #: Add to sys.path
        sys.path.append(lib)
        try:
            return f(enaml_qtbot, enaml_sleep, *args, **kwargs)
        finally:
            sys.path.remove(lib)

            #: Cleanup
            if os.path.exists(lib):
               os.remove(lib)

    return test_with_library


def assert_window_displays(enaml_qtbot, enaml_sleep, window):
    #: Make sure the imported library actually works
    window.show()
    window.send_to_front()
    wait_for_window_displayed(enaml_qtbot, window)
    enaml_qtbot.wait(enaml_sleep*1000)


@with_library
def test_zipimport_from_module(enaml_qtbot, enaml_sleep):
    with enaml.imports():
        # Test import from library.zip/buttons.enaml
        import buttons

    assert_window_displays(enaml_qtbot, enaml_sleep, buttons.Main())

@with_library
def test_zipimport_from_package(enaml_qtbot, enaml_sleep):
    with enaml.imports():
        # Test import from library.zip/package/form.enaml
        from package import form

    assert_window_displays(enaml_qtbot, enaml_sleep, form.Main())


@with_library
def test_zipimport_from_subpackage(enaml_qtbot, enaml_sleep):
    with enaml.imports():
        # Test import from library.zip/package/subpackage/slider.enaml
        from package.subpackage import slider

    assert_window_displays(enaml_qtbot, enaml_sleep, slider.Main())


@with_library
def test_zipimport_module_from_cache(enaml_qtbot, enaml_sleep):
    with enaml.imports():
        # Test import from library.zip/__enamlcache__/slider-enaml-py<ver>-cv<ver>.enamlc
        import splitter

    assert_window_displays(enaml_qtbot, enaml_sleep, splitter.Main())


@with_library
def test_zipimport_package_from_cache(enaml_qtbot, enaml_sleep):
    with enaml.imports():
        # Test import from enamlcache subpackage within zip
        # Test import from library.zip/package/subpackage/__enamlcache__/notebook-enaml-py<ver>-cv<ver>.enamlc
        from package.subpackage import notebook
    assert_window_displays(enaml_qtbot, enaml_sleep, notebook.Main())
