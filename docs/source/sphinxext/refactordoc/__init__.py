#------------------------------------------------------------------------------
#  file: refactor_doc.py
#  License: LICENSE.TXT
#
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from function_doc import FunctionDoc
from class_doc import ClassDoc
from enaml_decl_doc import EnamlDeclDoc

#------------------------------------------------------------------------------
# Extension definition
#------------------------------------------------------------------------------
def refactor_docstring(app, what, name, obj, options, lines):

    verbose = False
    # if 'component.Component' in name:
        # verbose = True

    if ('class' in what):
        ClassDoc(lines, verbose=verbose)
    elif ('function' in what) or ('method' in what):
        FunctionDoc(lines, verbose=verbose)
    elif ('enaml_decl' in what):
        EnamlDeclDoc(lines, verbose=verbose)

def setup(app):
    app.setup_extension('sphinx.ext.autodoc')
    app.connect('autodoc-process-docstring', refactor_docstring)
