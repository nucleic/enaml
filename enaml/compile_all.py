#------------------------------------------------------------------------------
# Copyright (c) 2018, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
""" Command-line tool to compile .py and .enaml files.

"""
import os
import sys
import compileall

from enaml.core.import_hooks import EnamlImporter, make_file_info


# We redefine this so create a local reference
compile_py_file = compileall.compile_file


def compile_enaml_file(fullname, ddir=None, force=0, rx=None, quiet=0,
                       *args, **kwargs):
    """Byte-compile one file using the EnamlImporter.

    """
    fullname = os.path.abspath(fullname)
    importer = EnamlImporter(make_file_info(fullname))
    if not quiet:
        print('Compiling {}...'.format(fullname))
    try:
        if force:
            importer.compile_code()
        else:
            importer.get_code()
        return True
    except Exception as e:
        if quiet:
            print('Compiling {}...'.format(fullname))
        print(str(e))
    # Failed
    return False


def compile_file(fullname, ddir=None, force=0, rx=None, quiet=0,
                 *args, **kwargs):
    """Byte-compile one file. Invokes the standard compiler for
    py files and the enaml compiler for enaml files.

    Parameters
    ----------
    fullname:  String
        the file to byte-compile
    ddir: String
        if given, the directory name compiled in to the
        byte-code file.
    force: Bool
        if True, force compilation, even if timestamps are up-to-date
    quiet: Bool
        full output with False or 0, errors only with 1,
        no output with 2

    """
    name = os.path.basename(fullname)
    if os.path.isfile(fullname):
        head, tail = os.path.splitext(name)
        if tail == '.py':
            return compile_py_file(fullname, ddir, force, rx, quiet,
                                   *args, **kwargs)
        elif tail == '.enaml':
            return compile_enaml_file(fullname, ddir, force, rx, quiet,
                                      *args, **kwargs)
    return True


if compileall.compile_file != compile_file:
    # Patch to use enaml
    compileall.compile_file = compile_file


def main():
    exit_status = int(not compileall.main())
    sys.exit(exit_status)


if __name__ == '__main__':
    main()
