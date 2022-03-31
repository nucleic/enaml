#------------------------------------------------------------------------------
# Copyright (c) 2013-2022, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import sys
import inspect
from setuptools import Extension, setup
from setuptools.command.install import install
from setuptools.command.develop import develop

from cppy import CppyBuildExt

# Use the env var ENAML_DISABLE_FH4 to disable linking against VCRUNTIME140_1.dll

ext_modules = [
    Extension(
        'enaml.weakmethod',
        ['enaml/src/weakmethod.cpp'],
        language='c++',
    ),
    Extension(
        'enaml.callableref',
        ['enaml/src/callableref.cpp'],
        language='c++',
    ),
    Extension(
       'enaml.signaling',
       ['enaml/src/signaling.cpp'],
       language='c++',
    ),
    Extension(
        'enaml.core.funchelper',
        ['enaml/src/funchelper.cpp'],
        language='c++',
    ),
    Extension(
        'enaml.colorext',
        ['enaml/src/colorext.cpp'],
        language='c++',
    ),
    Extension(
        'enaml.fontext',
        ['enaml/src/fontext.cpp'],
        language='c++',
    ),
    Extension(
        'enaml.core.dynamicscope',
        ['enaml/src/dynamicscope.cpp'],
        language='c++',
    ),
    Extension(
        'enaml.core.alias',
        ['enaml/src/alias.cpp'],
        language='c++',
    ),
    Extension(
        'enaml.core.declarative_function',
        ['enaml/src/declarative_function.cpp'],
        language='c++',
    ),
]


if sys.platform == 'win32':
    ext_modules.append(
        Extension(
            'enaml.winutil',
            ['enaml/src/winutil.cpp'],
            libraries=['user32', 'gdi32'],
            language='c++'
        )
    )


class Install(install):
    """ Calls the parser to construct a lex and parse table specific
        to the system before installation.

    """

    def run(self):
        try:
            from enaml.core.parser import write_tables
            write_tables()
        except ImportError:
            pass
        # Follow logic used in setuptools
        # cf https://github.com/pypa/setuptools/blob/master/setuptools/command/install.py#L58
        if self.old_and_unmanageable or self.single_version_externally_managed:
            return install.run(self)

        if not self._called_from_setup(inspect.currentframe()):
            # Run in backward-compatibility mode to support bdist_* commands.
            install.run(self)
        else:
            self.do_egg_install()


class Develop(develop):
    """ Calls the parser to construct a lex and parse table specific
        to the system before installation.

    """

    def run(self):
        try:
            from enaml.core.parser import write_tables
            write_tables()
        except ImportError:
            pass
        develop.run(self)


setup(
    ext_modules=ext_modules,
    cmdclass={'build_ext': CppyBuildExt,
              'install': Install,
              'develop': Develop},
)
