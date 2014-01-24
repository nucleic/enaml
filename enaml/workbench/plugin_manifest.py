#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import json
import os
import warnings

from atom.api import Atom, List, Typed

from .extension import Extension
from .extension_point import ExtensionPoint


class PluginManifest(Atom):
    """ A class which represents a plugin manifest.

    A PluginManifest and its data should be treated as read-only.

    """
    #: The dict of data loaded from the json declaration.
    data = Typed(dict)

    #: The list of extension points exposed by the plugin.
    extension_points = List(ExtensionPoint)

    #: The list of extensions contributed by the plugin.
    extensions = List(Extension)

    @property
    def id(self):
        """ Get the plugin identifer.

        """
        return self.data[u'id']

    @property
    def cls(self):
        """ Get the path of the class which implements the plugin.

        """
        return self.data.get(u'class', u'')

    @property
    def name(self):
        """ Get the human readable name of the plugin.

        """
        return self.data.get(u'name', u'')

    @property
    def description(self):
        """ Get the human readable description of the plugin.

        """
        return self.data.get(u'description', u'')


class ManifestValidator(object):
    """ A helper class for validating plugin manifest JSON data.

    This class should not be used directly by user code.

    """
    #: A reference to the singleton validator instance.
    __instance__ = None

    @staticmethod
    def load_validator():
        """ Load the schema validator function.

        Returns
        -------
        result : callable
            A callable which validates the schema. It will have a
            call signature which matches jsonschema.validate.

        """
        try:
            import jsonschema
        except:
            msg = "The 'jsonschema' package is not installed. "
            msg += "Plugin manifest validation will be skipped."
            warnings.warn(msg)
            validator = lambda i, s, c=None, *a, **k: None
        else:
            validator = jsonschema.validate
        return validator

    @staticmethod
    def load_schema():
        """ Load the schema data from the schema file.

        Returns
        -------
        result : object
            The schema data object.

        """
        abspath = os.path.abspath(__file__)
        dirname = os.path.dirname(abspath)
        path = os.path.join(dirname, 'schema.json')
        with open(path) as f:
            data = f.read()
        return json.loads(data)

    @classmethod
    def instance(cls):
        """ Get a reference to a singleton validator instance.

        Returns
        -------
        result : ManifestValidator
            A reference to a singleton validator instance.

        """
        if cls.__instance__ is None:
            cls.__instance__ = cls()
        return cls.__instance__

    def __init__(self):
        """ Initialize a ManifestValidator.

        """
        self._validator = self.load_validator()
        self._schema = self.load_schema()

    def __call__(self, instance):
        """ Validate the JSON data instance.

        This method will validate the instance against the plugin
        manifest schema.

        Parameters
        ----------
        instance : object
            The root object loaded from the JSON file.

        """
        self._validator(instance, self._schema)


def create_manifest(data, validate):
    """ Create a plugin manifest from JSON data.

    This function should not be used directly by user code.

    Parameters
    ----------
    data : str or unicode
        The json manifest data. If this is a str, it must be encoded
        in UTF-8 or plain ASCII.

    validate : bool
        Whether to validate the json against the manifest schema. This
        requires the 'jsonschema' package to be installed.

    Returns
    -------
    result : PluginManifest
        The manifest object for the given JSON data.

    """
    root = json.loads(data)
    if validate:
        ManifestValidator.instance()(root)
    return PluginManifest(data=root)
