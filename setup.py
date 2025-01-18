#------------------------------------------------------------------------------
# Copyright (c) 2013-2024, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import sys
from setuptools import Extension, setup
from setuptools.command.build_py import build_py
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
    Extension(
        'enaml.core.subscription_observer',
        ['enaml/src/subscription_observer.cpp'],
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


setup(
    use_scm_version=True,
    ext_modules=ext_modules,
    cmdclass={'build_ext': CppyBuildExt},
)
