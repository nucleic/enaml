#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
""" Generate the Example Documentation for the Enaml Examples

Run as part of the documentation build script. Requires PyQt4.
Look for example enaml files with the line:

<< autodoc-me >>

Generate an rst file, then open the app and take a snapshot.

"""
from __future__ import print_function
import os
os.environ['QT_API'] = 'pyqt'
import shutil

from atom.api import Atom, Unicode, Value
import enaml
from enaml.qt.qt_application import QtApplication
from enaml.qt.QtGui import QPixmap
from enaml.qt.QtWidgets import QApplication
from enaml.application import timed_call


class SnapShot(Atom):
    """ Generate a snapshot of an enaml view.

    """

    #: The snapshot save path.
    path = Unicode()

    #: The enaml view object.
    view = Value()

    def _observe_view(self, change):
        """ Move window and allow it to draw before taking the snapshot.

        """
        if change['type'] == 'create':
            self.view.initial_position = (10, 10)
            self.view.always_on_top = True
            timed_call(1500, self.snapshot)

    def snapshot(self):
        """ Take a snapshot of the window and close it.

        """
        widget = self.view.proxy.widget
        framesize =  widget.window().frameSize()
        QPixmap.grabWindow(QApplication.desktop().winId(), widget.x(),
                           widget.y(), framesize.width(),
                           framesize.height() ).save(self.path)
        self.view.close()


def generate_example_doc(app, docs_path, script_path):
    """ Generate an RST and a PNG for an example file.

    Parameters
    ----------
    app : QtApplication instance
    docs_path : str
         Full path to enaml/docs/source/examples
    script_path : str
         Full path to the example enaml file
    """
    script_name = os.path.basename(script_path)
    script_name = script_name[:script_name.find('.')]
    print('generating doc for %s' % script_name)

    script_title = script_name.replace('_', ' ').title()
    script_image_name = 'ex_' + script_name + '.png'
    image_path = os.path.join(docs_path, 'images', script_image_name)
    rst_path = os.path.join(
        docs_path, 'ex_' + script_name + '.rst')
    relative_script_path = script_path[
        script_path.find('examples'):].replace('\\', '/')

    with open(os.path.join(script_path)) as fid:
        script_text = fid.read()

    docstring = script_text[script_text.find('"""') + 3:]
    docstring = docstring[: docstring.find('"""')]
    docstring = docstring.replace('<< autodoc-me >>\n', '').strip()

    rst_template = """
{0} Example
===============================================================================

:download:`{1} <../../../{2}>`

::

    {3}

::

 $ enaml-run {1}

.. image:: images/{4}

.. literalinclude:: ../../../{2}
    :language: enaml

""".format(script_title, script_name, relative_script_path,
           docstring.replace('\n', '\n    '), script_image_name)

    with open(rst_path, 'wb') as fid:
        fid.write(rst_template.lstrip().encode())

    temp_path = os.path.join(docs_path, os.path.basename(script_path))

    with open(temp_path, 'wb') as fid:
        fid.write(script_text.encode())

    with enaml.imports():
        try:
            mod = __import__(script_name)
        except Exception as err:
            print('Could not create: %s' % script_name)
            print('    %s' % err)
            os.remove(temp_path)
            return
    try:
        view = mod.Main()
        snapshot = SnapShot(path=image_path, view=view)
        view.show()
        app.start()
    except Exception as err:
        print('Could not create: %s' % script_name)
        print('    %s' % err)
    finally:
        os.remove(temp_path)


def main():
    """ Generate documentation for all enaml examples requesting autodoc.

    Looks in enaml/examples for all enaml files, then looks for the line:
    << auto-doc >>

    If the line appears in the script, generate an RST and PNG for the example.
    """
    app = QtApplication()
    docs_path = os.path.dirname(__file__)
    base_path = '../../../examples'
    base_path = os.path.realpath(os.path.join(docs_path, base_path))

    enaml_cache_dir = os.path.join(docs_path, '__enamlcache__')

    for dirname, dirnames, filenames in os.walk(base_path):
        files = [os.path.join(dirname, f)
                 for f in filenames if f.endswith('.enaml')]
        for fname in files:
            with open(fname, 'rb') as fid:
                data = fid.read()
            if b'<< autodoc-me >>' in data.splitlines():
                try:
                    generate_example_doc(app, docs_path, fname)
                except KeyboardInterrupt:
                    shutil.rmtree(enaml_cache_dir)
                    return
    shutil.rmtree(enaml_cache_dir)


if __name__ == '__main__':
    main()
