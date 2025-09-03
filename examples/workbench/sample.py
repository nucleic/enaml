#------------------------------------------------------------------------------
# Copyright (c) 2013-2025, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
""" A simple example plugin application.

This example serves to demonstrate the concepts described the accompanying
developer crash source document.

"""
import enaml
from enaml.workbench.ui.api import UIWorkbench

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    with enaml.imports():
        from sample_plugin import SampleManifest

    workbench = UIWorkbench()
    workbench.register(SampleManifest())
    workbench.run()


if __name__ == '__main__':
    main()
