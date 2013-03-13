#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Str

from .enums import ItemFlag, AlignmentFlag


class ItemEditor(Atom):

    name = Str()

    def get_data(self, model):
        return None

    def get_flags(self, model):
        return ItemFlag.ItemIsSelectable | ItemFlag.ItemIsEnabled

    def get_edit_data(self, model):
        return self.get_data(model)

    def get_icon(self, model):
        return None

    def get_tool_tip(self, model):
        return None

    def get_status_tip(self, model):
        return None

    def get_background(self, model):
        return None

    def get_foreground(self, model):
        return None

    def get_font(self, model):
        return None

    def get_text_alignment(self, model):
        return AlignmentFlag.AlignCenter

    def get_check_state(self, model):
        return None

    def get_size_hint(self, model):
        return None

    def set_data(self, model, value):
        return False

    def set_check_state(self, model, value):
        return False


class AttrEditor(ItemEditor):

    def get_data(self, model):
        return getattr(model, self.name)

    def set_data(self, model, value):
        setattr(model, self.name, value)
