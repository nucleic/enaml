#------------------------------------------------------------------------------
# Copyright (c) 2013-2018, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import os
import sys
import inspect
from setuptools import find_packages, Extension, setup
from setuptools.command.build_ext import build_ext
from setuptools.command.install import install
from setuptools.command.develop import develop

sys.path.insert(0, os.path.abspath('.'))
from enaml.version import __version__

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
    Extension(
        'enaml.c_compat',
        ['enaml/src/c_compat.cpp'],
        language='c++',
    )
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


class BuildExt(build_ext):
    """ A custom build extension for adding compiler-specific options.

    """
    c_opts = {
        'msvc': ['/EHsc']
    }

    def initialize_options(self):
        build_ext.initialize_options(self)
        self.debug = False

    def build_extensions(self):
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])
        for ext in self.extensions:
            ext.extra_compile_args = opts
        build_ext.build_extensions(self)


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
    name='enaml',
    version=__version__,
    author='The Nucleic Development Team',
    author_email='sccolbert@gmail.com',
    url='https://github.com/nucleic/enaml',
    description='Declarative DSL for building rich user interfaces in Python',
    long_description=open('README.rst').read(),
    requires=['future', 'atom', 'PyQt', 'ply', 'kiwisolver', 'qtpy'],
    install_requires=['setuptools', 'future', 'atom>=0.4.1', 'qtpy>=1.3',
                      'kiwisolver>=1.0.0', 'ply>=3.4'],
    packages=find_packages(),
    package_data={
        'enaml.applib': ['*.enaml'],
        'enaml.stdlib': ['*.enaml'],
        'enaml.workbench.core': ['*.enaml'],
        'enaml.workbench.ui': ['*.enaml'],
        'enaml.qt.docking': [
            'dock_images/*.png',
            'dock_images/*.py',
            'enaml_dock_resources.qrc'
        ],
    },
    entry_points={'console_scripts': ['enaml-run = enaml.runner:main']},
    ext_modules=ext_modules,
    cmdclass={'install': Install,
              'develop': Develop},
)
