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


def _create_validator():
    if os.environ.get('ENAML_WORKBENCH_SCHEMA_VALIDATION'):
        try:
            import jsonschema
        except ImportError:
            msg = "The 'jsonschema' package is not installed. "
            msg += "Schema validation will be skipped."
            warnings.warn(msg)
        else:
            schemas = {}
            def validate(item, path):
                path = os.path.abspath(path)
                if path not in schemas:
                    with open(path) as f:
                        data = f.read()
                    schemas[path] = json.loads(data)
                jsonschema.validate(item, schemas[path])
            return validate
    return lambda item, schema: None

_validate = _create_validator()


def validate(item, path):
    """ Validate an object against a JSON schema.

    If the validation fails, an exception will be raised.

    Parameters
    ----------
    item : object
        An object loaded from a JSON file. This will usually be
        a dict.

    path : str
        The path to the JSON schema file.

    """
    _validate(item, path)
