import sys
import enaml

def with_library(f):
    #: Add and remove library.zip from the sys path
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
def test_zipimport_cache():
    with enaml.imports():
        # Test import from enamlcache file within zip
        import splitter
        
        # Test import from subpackage within zip
        from package.subpackage import notebook


@with_library
def main():
    from enaml.qt.qt_application import QtApplication
    
    with enaml.imports():
        #from buttons import Main
        #from package.subpackage.notebook import Main
        from package.subpackage.slider import Main

    app = QtApplication()

    view = Main()
    view.show()

    # Start the application event loop
    app.start()


if __name__ == "__main__":
    test_zipimport()
    test_zipimport_subpackage()
    test_zipimport_cache()
    main()
    
