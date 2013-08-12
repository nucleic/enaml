#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
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
    )
]


setup(
    name='enaml',
    version='0.7.20',
    author='The Nucleic Development Team',
    author_email='sccolbert@gmail.com',
    url='https://github.com/nucleic/enaml',
    description='Declarative DSL for building rich user interfaces in Python',
    long_description=open('README.md').read(),
    requires=['atom', 'PyQt', 'ply', 'casuarius'],
    install_requires=['distribute'],
    packages=find_packages(),
    package_data={
        'enaml.applib': ['*.enaml'],
        'enaml.stdlib': ['*.enaml'],
        'enaml.qt.docking': [
            'dock_images/*.png',
            'dock_images/*.py',
            'enaml_dock_resources.qrc'
        ],
    },
    entry_points={'console_scripts': ['enaml-run = enaml.runner:main']},
    ext_modules=ext_modules,
)
