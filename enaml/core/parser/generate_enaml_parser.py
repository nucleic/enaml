# --------------------------------------------------------------------------------------
# Copyright (c) 2022-2024, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# --------------------------------------------------------------------------------------
"""Script used to generate the Enaml parser from enaml.gram"""
import pathlib

from pegen.build import build_python_parser_and_generator


def main():

    # TODO add support for generating a verbose parser

    dir_path = pathlib.Path(__file__).parent
    build_python_parser_and_generator(
        str(dir_path / "enaml.gram"), str(dir_path / "enaml_parser.py")
    )

if __name__ == "__main__":
    main()
