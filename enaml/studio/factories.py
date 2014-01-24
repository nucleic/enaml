#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
""" A module of lazy import factories for enaml studio modules.

These loaders are used by the studio plugins to engage the enaml import
hook when loading the necessary enaml dependencies.

"""
import enaml


def StudioWindow(parent=None, **kwargs):
    with enaml.imports():
        from enaml.studio.studio_window import StudioWindow
    return StudioWindow(parent, **kwargs)
