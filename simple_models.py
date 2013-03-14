from atom.api import Atom, Int, Str

from enaml.colors import parse_color
from enaml.fonts import parse_font
from enaml.itemmodels.modeleditor import ModelEditor, EditGroup, AttrEditor
from enaml.itemmodels.editortablemodel import EditorTableModel

#------------------------------------------------------------------------------
# Custom Item Editors
#------------------------------------------------------------------------------
lightskyblue = parse_color('lightskyblue')
steelblue = parse_color('steelblue')
red = parse_color('red')
goldenrod = parse_color('goldenrod')

arial = parse_font('bold 12pt arial')
ariallarge = parse_font('bold italic 24pt times')


class BEditor(AttrEditor):

    def get_background(self, model):
        if model.b % 7 != 0:
            return lightskyblue
        return steelblue


class CEditor(AttrEditor):

    def get_foreground(self, model):
        return red

    def get_font(self, model):
        return arial


class EEditor(AttrEditor):

    def get_background(self, model):
        return goldenrod


class FEditor(AttrEditor):

    def get_font(self, model):
        return ariallarge

#------------------------------------------------------------------------------
# Data Models
#------------------------------------------------------------------------------
class Foo(Atom):
    name = Str()
    a = Int()
    b = Int()
    c = Int()

    edit_groups = [
        EditGroup(
            name='Ints',
            item_editors=[
                AttrEditor(name='name'),
                AttrEditor(name='a'),
                BEditor(name='b'),
                CEditor(name='c'),
            ]
        )
    ]


class Bar(Foo):
    d = Str()
    e = Str()
    i = Str()

    edit_groups = Foo.edit_groups + [
        EditGroup(
            name='Strings',
            item_editors=[
                AttrEditor(name='d'),
                EEditor(name='e'),
                AttrEditor(name='i'),
            ]
        )
    ]


class Baz(Bar):
    f = Int()
    g = Int()
    h = Int()

    edit_groups = Bar.edit_groups + [
        EditGroup(
            name='Ints',
            item_editors=[
                FEditor(name='f'),
                AttrEditor(name='g'),
                AttrEditor(name='i'),
            ]
        )
    ]


#------------------------------------------------------------------------------
# Data Object generation
#------------------------------------------------------------------------------
count = 0
models = []
for i in range(100000):
    si = str(i)
    f = Foo(name='item ' + str(count), a=i, b=i, c=i)
    b = Bar(name='item ' + str(count + 1), a=i, b=i, c=i, d='D ' + si, e='E ' + si, i='I ' + si)
    z = Baz(name='item ' + str(count + 2), a=i, b=i, c=i, d='D ' + si, e='E ' + si, i='I ' + si, f=i, g=i, h=i)
    models.append(f)
    models.append(b)
    models.append(z)
    count += 3


datamodel = EditorTableModel()
for m in models:
    datamodel.add_editor(ModelEditor(model=m, edit_groups=m.edit_groups))
import time
t1 = time.clock()
datamodel.layout()
t2 = time.clock()
print t2 - t1
