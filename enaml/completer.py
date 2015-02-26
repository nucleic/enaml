#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import os
from atom.api import Atom, List, Callable


class Completer(Atom):
    """ The base class for creating widget text completions.

    """
    #: A list of completion strings used by the widget
    completions = List()

    def update(self, text):
        """ Update the completions list as the user types.

        This method is called on every keystroke to update the list of
        completions.

        Parameters
        ----------
        text : unicode
            The unicode text entered by the user.
        """
        pass


class FileCompleter(Completer):
    """ A completer which completes on valid file system paths.

    """
    def update(self, text):
        """ Update the completions list to include valid system paths.

        Parameters
        ----------
        text : unicode
            The unicode text entered by the user.
        """
        dname = os.path.dirname(text)
        base = os.path.basename(text)
        if os.path.exists(dname):
            files = os.listdir(dname)
            if base:
                files = [f[len(base):] for f in files if f.startswith(base)]
            c = [text + f for f in files]
            self.completions = c


class DirectoryCompleter(Completer):
    """ A completer which completes on valid file system directories.

    """
    def update(self, text):
        """ Update the completions list to include valid system directories.

        Parameters
        ----------
        text : unicode
            The unicode text entered by the user.
        """
        dname = os.path.dirname(text)
        base = os.path.basename(text)
        if os.path.exists(dname):
            files = os.listdir(dname)
            if base:
                files = [f[len(base):] for f in files if f.startswith(base)]
            c = [text + f for f in files]
            self.completions = [p for p in c if os.path.isdir(p)]


class CustomCompleter(Completer):
    """ A completer which calls a user-provided callable to set completions.

    """
    #: A user-defined callable which accepts the current text and 
    #: returns a list of completions
    callback = Callable()

    def update(self, text):
        """ Update the completions list using user-defined callable.

        Parameters
        ----------
        text : unicode
            The unicode text entered by the user.
        """
        if self.callback:
            self.completions = self.callback(text)
