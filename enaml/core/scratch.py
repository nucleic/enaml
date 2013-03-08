    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def initialize(self):
        """ Initialize this object all of its children recursively.

        This is called to give the objects in the tree the opportunity
        to initialize additional state which depends upon the object
        tree being fully built. It is the responsibility of external
        code to call this method at the appropriate time. This will
        emit the `initialized` signal after all of the children have
        been initialized.

        """
        # Initialization is performed by iterating over a copy of the
        # children since a child may add new children to this object.
        # At that point, the child which added the new children is
        # repsonsible for initializing them.
        self.lifecycle = 'initializing'
        for child in self._children[:]:
            child.initialize()
        self.lifecycle = 'initialized'
        self.initialized()