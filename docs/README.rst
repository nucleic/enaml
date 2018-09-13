Building the docs
=================

Building the docs involve the following steps:

- install enaml and its required dependencies: ply, qtpy, atom, kwisolver
- install sphinx and sphinx_rtd_theme
- install the enaml lexer for pygments: pip install pygments-enaml
- cd into the docs folder and run `make html`

Rebuilding the example pages and screenshot involve the following steps:

- install enaml and its required dependencies: ply, qtpy, atom, kiwisolver
- install in addition: pyqt, numpy, matplotlib, ipython, qtconsole, vtk,
  qscintilla
- cd into the docs folder and run `make examples`

