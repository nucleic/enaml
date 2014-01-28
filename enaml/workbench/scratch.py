    def get_extension(self, extension_point_id, extension_id):
        """ Get a specific extension contributed to an extension point.

        If the specified extension point has not been registered, this
        method will always return None

        Parameters
        ----------
        extension_point_id : unicode
            The fully qualified id of the extension point to of interest.

        extension_id : unicode
            The fully qualified id of the extension.

        Returns
        -------
        result : Extension or None
            The requested Extension, or None if it does not exist.

        """
        if extension_point_id not in self._extension_points:
            return None
        for extension in self._contributions.get(extension_point_id, ()):
            if extension.qualified_id == extension_id:
                return extension
        return None

    def get_extensions(self, extension_point_id):
        """ Get the extensions contributed to an extension point.

        If the specified extension point has not been registered, this
        method will always return an empty list.

        Parameters
        ----------
        extension_point_id : unicode
            The fully qualified id of the extension point of interest.

        Returns
        -------
        result : list
            A list of Extensions contributed to the extension point.

        """
        if extension_point_id not in self._extension_points:
            return []
        extensions = self._contributions.get(extension_point_id)
        return extensions[:] if extensions else []
