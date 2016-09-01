#------------------------------------------------------------------------------
# Copyright (c) 2016, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import sys
import enaml

def with_library(f):
    # Add and remove library.zip from the sys path
    def wrapped(*args,**kwargs):
        sys.path.append('library.zip')
        try:
            return f(*args,**kwargs)
        finally:
            sys.path.remove('library.zip')
    return wrapped

@with_library
def test_zipimport():
    with enaml.imports():
        # Test import from libary.zip/buttons.enaml
        import buttons

@with_library  
def test_zipimport_subpackage():
    with enaml.imports():
        # Test import from libary.zip/package/form.enaml
        from package import form
        
        # Test import from libary.zip/package/subpackage/slider.enaml
        from package.subpackage import slider


@with_library
def main():
    from enaml.qt.qt_application import QtApplication
    
    with enaml.imports():
        #from buttons import Main
        from package.subpackage.slider import Main

    app = QtApplication()

    view = Main()
    view.show()

    # Start the application event loop
    app.start()


if __name__ == "__main__":
    test_zipimport()
    test_zipimport_subpackage()
    main()
    
