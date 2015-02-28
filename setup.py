#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import sys
from setuptools import setup, find_packages, Extension


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


setup(
    name='enaml',
    version='0.9.8',
    author='The Nucleic Development Team',
    author_email='sccolbert@gmail.com',
    url='https://github.com/nucleic/enaml',
    description='Declarative DSL for building rich user interfaces in Python',
    long_description=open('README.rst').read(),
    requires=['atom', 'PyQt', 'ply', 'kiwisolver'],
    install_requires=['distribute', 'atom >= 0.3.8', 'kiwisolver >= 0.1.2', 'ply >= 3.4'],
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
)
