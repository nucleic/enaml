from atom.api import Atom, Int, Float, Str

from enaml.colors import parse_color
from enaml.itemmodels.api import (
    Editor, Group, Item, IntItem, StrItem, FloatItem, EditorTable
)

#------------------------------------------------------------------------------
# Custom Items
#------------------------------------------------------------------------------
lightskyblue = parse_color('lightskyblue')
steelblue = parse_color('steelblue')

class AltBlue(Item):

    def get_background(self, model):
        if getattr(model, self.name) % 7 != 0:
            return lightskyblue
        return steelblue


#------------------------------------------------------------------------------
# Data Models
#------------------------------------------------------------------------------
class Foo(Atom):
    name = Str()
    a = Int()
    b = Int()
    c = Int()

    groups = [
        Group('Ints',
            items=[
                StrItem('name'),
                IntItem('a'),
                AltBlue('b'),
                IntItem('c', foreground='red', font='bold 12pt arial'),
            ]
        )
    ]


class Bar(Foo):
    d = Str()
    e = Str()
    i = Str()

    groups = Foo.groups + [
        Group('Strings',
            items=[
                StrItem('d'),
                StrItem('e', background='goldenrod'),
                StrItem('i'),
            ]
        )
    ]


class Baz(Bar):
    f = Int()
    g = Float()
    h = Int()

    groups = Bar.groups + [
        Group('Ints',
            items=[
                IntItem('f', font='bold italic 24pt times'),
                FloatItem('g'),
                IntItem('i'),
            ]
        )
    ]


#------------------------------------------------------------------------------
# Data Object generation
#------------------------------------------------------------------------------
count = 0
models = []
for i in range(10000):
    si = str(i)
    f = Foo(name='item ' + str(count), a=i, b=i, c=i)
    b = Bar(name='item ' + str(count + 1), a=i, b=i, c=i, d='D ' + si, e='E ' + si, i='I ' + si)
    z = Baz(name='item ' + str(count + 2), a=i, b=i, c=i, d='D ' + si, e='E ' + si, i='I ' + si, f=i, g=i, h=i)
    models.append(f)
    models.append(b)
    models.append(z)
    count += 3


datamodel = EditorTable()
for m in models:
    datamodel.add_editor(Editor(model=m, groups=m.groups))

import time
t1 = time.clock()
datamodel.layout()
t2 = time.clock()
print t2 - t1
