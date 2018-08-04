Building the docs
=================

Building the docs involve the following steps:

- install enaml and its required dependencies: ply, qtpy, atom, kwisolver
- install sphinx
- install the enamllexer for pygments by going to tools/pygments and running
  python setup.py install
- cd into the docs folder and run `make html`

Rebuilding the example pages and screenshot involve the following steps:

- install enaml and its required dependencies: ply, qtpy, atom, kiwisolver
- install in addition: pyqt, numpy, matplotlib, ipython, qtconsole, vtk,
  qscintilla
- cd into the docs folder and run `make examples`

