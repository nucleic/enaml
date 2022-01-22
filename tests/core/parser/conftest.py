# ------------------------------------------------------------------------------
# Copyright (c) 2018-2022, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------
import os
import pathlib

import pytest


@pytest.fixture(scope="session", autouse=True)
def validate_parser_is_up_to_date():
    """Check that the generated parser is up to date with its sources."""
    from enaml.core.parser import base_enaml_parser, base_python_parser, enaml_parser

    last_source_modif = max(
        os.getmtime(base_enaml_parser.__file__),
        os.getmtime(base_python_parser.__file__),
        os.getmtime(pathlib.Path(base_enaml_parser.__file__).parent / "enaml.gram"),
    )

    assert os.getmtime(enaml_parser.__file__) >= last_source_modif, "Generated parser appears outdated compared to its sources, re-generate it using enaml/core/parser/generate_enaml_parser.enaml"
