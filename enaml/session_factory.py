#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
class SessionFactory(object):
    """ A class whose instances are used by an Enaml Application to
    create Session instances.

    """
    def __init__(self, name, description, session_class, *args, **kwargs):
        """ Initialize a SessionFactory.

        Parameters
        ----------
        name : str
            A unique, human-friendly name for the Session that will be
            created.

        description : str
            A brief description of the Session that will be created.

        session_class : Session subclass
            A concrete subclass of Session that will be created by this
            factory.

        *args, **kwargs
            Optional positional and keyword arguments to pass to the
            __init__() method of the Session that gets created.

        """
        self.name = name
        self.description = description
        self.session_class = session_class
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        """ Called by the Enaml Application to create an instance of
        the Session.

        Returns
        -------
        result : Session
            A new instance of the Session type provided to the factory.

        """
        return self.session_class(*self.args, **self.kwargs)

