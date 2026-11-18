import test
import a, b
import test as t
import test as t, y
import test.a
import test.a, test.b
import test.b as b


from test import a
from test import a, b
from test import (
    a,
    b,
)
from test import a as b
from test import a as b, c
from test import a as b, c as d
from test import *
from test.a import b
from test.a import b as c
from test.a import b, c
from test.a import b as c, d


from . import a
from ... import b
from .... import c
from ..a import b
from ...a import c
from ....a import c
from . import a, b
from ..a import b, c
from ...a import c, d
from ....a import c, d
