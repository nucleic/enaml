match 0:
    case 0:
        x = True



match 0:
    case 0 if False:
        x = False
    case 0 if True:
        x = True



match 0:
    case 0:
        x = True
    case 0:
        x = False



x = False
match 0:
    case 0 | 1 | 2 | 3:
        x = True



x = False
match 1:
    case 0 | 1 | 2 | 3:
        x = True



x = False
match 2:
    case 0 | 1 | 2 | 3:
        x = True



x = False
match 3:
    case 0 | 1 | 2 | 3:
        x = True



x = False
match 4:
    case 0 | 1 | 2 | 3:
        x = True



x = 0
class A:
    y = 1
match x:
    case A.y:
        pass



x = 0
class A:
    y = 1
match x:
    case A.y as z:
        pass



class A:
    B = 0
match 0:
    case x if x:
        z = 0
    case _ as y if y == x and y:
        z = 1
    case A.B:
        z = 2



match ():
    case []:
        x = 0



match (0, 1, 2):
    case [*x]:
        y = 0



match (0, 1, 2):
    case [0, *x]:
        y = 0



match (0, 1, 2):
    case [0, 1, *x,]:
        y = 0



match (0, 1, 2):
    case [0, 1, 2, *x]:
        y = 0



match (0, 1, 2):
    case [*x, 2,]:
        y = 0



match (0, 1, 2):
    case [*x, 1, 2]:
        y = 0



match (0, 1, 2):
    case [*x, 0, 1, 2,]:
        y = 0



match (0, 1, 2):
    case [0, *x, 2]:
        y = 0



match (0, 1, 2):
    case [0, 1, *x, 2,]:
        y = 0



match (0, 1, 2):
    case [0, *x, 1, 2]:
        y = 0



match (0, 1, 2):
    case [*x,]:
        y = 0



x = {}
match x:
    case {}:
        y = 0



x = {0: 0}
match x:
    case {}:
        y = 0



x = {}
y = None
match x:
    case {0: 0}:
        y = 0



x = {0: 0}
match x:
    case {0: (0 | 1 | 2 as z)}:
        y = 0



x = {0: 1}
match x:
    case {0: (0 | 1 | 2 as z)}:
        y = 0



x = {0: 2}
match x:
    case {0: (0 | 1 | 2 as z)}:
        y = 0



x = {0: 3}
y = None
match x:
    case {0: (0 | 1 | 2 as z)}:
        y = 0



x = {}
y = None
match x:
    case {0: [1, 2, {}]}:
        y = 0
    case {0: [1, 2, {}], 1: [[]]}:
        y = 1
    case []:
        y = 2



x = {False: (True, 2.0, {})}
match x:
    case {0: [1, 2, {}]}:
        y = 0
    case {0: [1, 2, {}], 1: [[]]}:
        y = 1
    case []:
        y = 2



x = {False: (True, 2.0, {}), 1: [[]], 2: 0}
match x:
    case {0: [1, 2, {}]}:
        y = 0
    case {0: [1, 2, {}], 1: [[]]}:
        y = 1
    case []:
        y = 2



x = {False: (True, 2.0, {}), 1: [[]], 2: 0}
match x:
    case {0: [1, 2]}:
        y = 0
    case {0: [1, 2, {}], 1: [[]]}:
        y = 1
    case []:
        y = 2



x = []
match x:
    case {0: [1, 2, {}]}:
        y = 0
    case {0: [1, 2, {}], 1: [[]]}:
        y = 1
    case []:
        y = 2



x = {0: 0}
match x:
    case {0: [1, 2, {}]}:
        y = 0
    case {0: ([1, 2, {}] | False)} | {1: [[]]} | {0: [1, 2, {}]} | [] | "X" | {}:
        y = 1
    case []:
        y = 2



x = {0: 0}
match x:
    case {0: [1, 2, {}]}:
        y = 0
    case {0: [1, 2, {}] | True} | {1: [[]]} | {0: [1, 2, {}]} | [] | "X" | {}:
        y = 1
    case []:
        y = 2



x = {0: 0}
match x:
    case {None: 1}:
        y = 0
    case {True: 1}:
        y = 0
    case {False: 1}:
        y = 0
    case {1 + 1j: 1}:
        y = 0
    case {a.b: 1}:
        y = 0



x = 0
match x:
    case 0 | 1 | 2:
        y = 0



x = 1
match x:
    case 0 | 1 | 2:
        y = 0



x = 2
match x:
    case 0 | 1 | 2:
        y = 0



x = 3
y = None
match x:
    case 0 | 1 | 2:
        y = 0



x = 0
match x:
    case (0 as z) | (1 as z) | (2 as z) if z == x % 2:
        y = 0



x = 1
match x:
    case (0 as z) | (1 as z) | (2 as z) if z == x % 2:
        y = 0



x = 2
y = None
match x:
    case (0 as z) | (1 as z) | (2 as z) if z == x % 2:
        y = 0



x = 3
y = None
match x:
    case (0 as z) | (1 as z) | (2 as z) if z == x % 2:
        y = 0



x = ()
match x:
    case []:
        y = 0



x = ()
match x:
    case ():
        y = 0



x = (0,)
match x:
    case [0]:
        y = 0



x = ((),)
match x:
    case [[]]:
        y = 0



x = [0, 1]
match x:
    case [0, 1] | [1, 0]:
        y = 0



x = [1, 0]
match x:
    case [0, 1] | [1, 0]:
        y = 0



x = [0, 0]
y = None
match x:
    case [0, 1] | [1, 0]:
        y = 0



w = None
x = [1, 0]
match x:
    case [(0 as w)]:
        y = 0
    case [z] | [1, (0 | 1 as z)] | [z]:
        y = 1



x = [1, 0]
match x:
    case [0]:
        y = 0
    case [1, 0] if (x := x[:0]):
        y = 1
    case [1, 0]:
        y = 2



x = {0}
y = None
match x:
    case [0]:
        y = 0



x = set()
y = None
match x:
    case []:
        y = 0



x = iter([1, 2, 3])
y = None
match x:
    case []:
        y = 0



x = {}
y = None
match x:
    case []:
        y = 0



x = {0: False, 1: True}
y = None
match x:
    case [0, 1]:
        y = 0



x = 0
match x:
    case 0:
        y = 0



x = 0
y = None
match x:
    case False:
        y = 0



x = 0
y = None
match x:
    case 1:
        y = 0



x = 0
y = None
match x:
    case None:
        y = 0



x = 0
match x:
    case 0:
        y = 0
    case 0:
        y = 1



x = 0
y = None
match x:
    case 1:
        y = 0
    case 1:
        y = 1



x = "x"
match x:
    case "x":
        y = 0
    case "y":
        y = 1



x = "x"
match x:
    case "y":
        y = 0
    case "x":
        y = 1



x = "x"
match x:
    case "":
        y = 0
    case "x":
        y = 1



x = b"x"
match x:
    case b"y":
        y = 0
    case b"x":
        y = 1



x = 0
match x:
    case 0 if False:
        y = 0
    case 0:
        y = 1



x = 0
y = None
match x:
    case 0 if 0:
        y = 0
    case 0 if 0:
        y = 1



x = 0
match x:
    case 0 if True:
        y = 0
    case 0 if True:
        y = 1



x = 0
match x:
    case 0 if 1:
        y = 0
    case 0 if 1:
        y = 1



x = 0
match x:
    case 0 if True:
        y = 0
    case 0 if True:
        y = 1
y = 2



x = 0
match x:
    case 0 if 0:
        y = 0
    case 0 if 1:
        y = 1
y = 2



x = 0
y = None
match x:
    case 0 if not (x := 1):
        y = 0
    case 1:
        y = 1



x = "x"
match x:
    case ["x"]:
        y = 0
    case "x":
        y = 1



x = b"x"
match x:
    case [b"x"]:
        y = 0
    case ["x"]:
        y = 1
    case [120]:
        y = 2
    case b"x":
        y = 4



x = bytearray(b"x")
y = None
match x:
    case [120]:
        y = 0
    case 120:
        y = 1



x = ""
match x:
    case []:
        y = 0
    case [""]:
        y = 1
    case "":
        y = 2



x = "xxx"
match x:
    case ["x", "x", "x"]:
        y = 0
    case ["xxx"]:
        y = 1
    case "xxx":
        y = 2



x = b"xxx"
match x:
    case [120, 120, 120]:
        y = 0
    case [b"xxx"]:
        y = 1
    case b"xxx":
        y = 2



x = 0
match x:
    case 0 if not (x := 1):
        y = 0
    case (0 as z):
        y = 1



x = 0
match x:
    case (1 as z) if not (x := 1):
        y = 0
    case 0:
        y = 1



x = 0
match x:
    case (0 as z):
        y = 0



x = 0
y = None
match x:
    case (1 as z):
        y = 0



x = 0
y = None
match x:
    case (0 as z) if (w := 0):
        y = 0



x = 0
match x:
    case ((0 as w) as z):
        y = 0



x = 0
match x:
    case (0 | 1) | 2:
        y = 0



x = 1
match x:
    case (0 | 1) | 2:
        y = 0



x = 2
match x:
    case (0 | 1) | 2:
        y = 0



x = 3
y = None
match x:
    case (0 | 1) | 2:
        y = 0



x = 0
match x:
    case 0 | (1 | 2):
        y = 0



x = 1
match x:
    case 0 | (1 | 2):
        y = 0



x = 2
match x:
    case 0 | (1 | 2):
        y = 0



x = 3
y = None
match x:
    case 0 | (1 | 2):
        y = 0



x = 0
match x:
    case -0:
        y = 0



x = 0
match x:
    case -0.0:
        y = 0



x = 0
match x:
    case -0j:
        y = 0



x = 0
match x:
    case -0.0j:
        y = 0



x = -1
match x:
    case -1:
        y = 0



x = -1.5
match x:
    case -1.5:
        y = 0



x = -1j
match x:
    case -1j:
        y = 0



x = -1.5j
match x:
    case -1.5j:
        y = 0



x = 0
match x:
    case 0 + 0j:
        y = 0



x = 0
match x:
    case 0 - 0j:
        y = 0



x = 0
match x:
    case -0 + 0j:
        y = 0



x = 0
match x:
    case -0 - 0j:
        y = 0



x = 0.25 + 1.75j
match x:
    case 0.25 + 1.75j:
        y = 0



x = 0.25 - 1.75j
match x:
    case 0.25 - 1.75j:
        y = 0



x = -0.25 + 1.75j
match x:
    case -0.25 + 1.75j:
        y = 0



x = -0.25 - 1.75j
match x:
    case -0.25 - 1.75j:
        y = 0



class A:
    B = 0
x = 0
match x:
    case A.B:
        y = 0



class A:
    class B:
        C = 0
x = 0
match x:
    case A.B.C:
        y = 0



class A:
    class B:
        C = 0
        D = 1
x = 1
match x:
    case A.B.C:
        y = 0
    case A.B.D:
        y = 1



class A:
    class B:
        class C:
            D = 0
x = 0
match x:
    case A.B.C.D:
        y = 0



class A:
    class B:
        class C:
            D = 0
            E = 1
x = 1
match x:
    case A.B.C.D:
        y = 0
    case A.B.C.E:
        y = 1



match = case = 0
match match:
    case case:
        x = 0



match = case = 0
match case:
    case match:
        x = 0



x = []
match x:
    case [*_, _]:
        y = 0
    case []:
        y = 1



x = collections.defaultdict(int)
match x:
    case {0: 0}:
        y = 0
    case {}:
        y = 1



x = collections.defaultdict(int)
match x:
    case {0: 0}:
        y = 0
    case {**z}:
        y = 1



match ():
    case ():
        x = 0



match (0, 1, 2):
    case (*x,):
        y = 0



match (0, 1, 2):
    case 0, *x:
        y = 0



match (0, 1, 2):
    case (0, 1, *x,):
        y = 0



match (0, 1, 2):
    case 0, 1, 2, *x:
        y = 0



match (0, 1, 2):
    case *x, 2,:
        y = 0



match (0, 1, 2):
    case (*x, 1, 2):
        y = 0



match (0, 1, 2):
    case *x, 0, 1, 2,:
        y = 0



match (0, 1, 2):
    case (0, *x, 2):
        y = 0



match (0, 1, 2):
    case 0, 1, *x, 2,:
        y = 0



match (0, 1, 2):
    case (0, *x, 1, 2):
        y = 0



match (0, 1, 2):
    case *x,:
        y = 0



x = collections.defaultdict(int, {0: 1})
match x:
    case {1: 0}:
        y = 0
    case {0: 0}:
        y = 1
    case {}:
        y = 2



x = collections.defaultdict(int, {0: 1})
match x:
    case {1: 0}:
        y = 0
    case {0: 0}:
        y = 1
    case {**z}:
        y = 2



x = collections.defaultdict(int, {0: 1})
match x:
    case {1: 0}:
        y = 0
    case {0: 0}:
        y = 1
    case {0: _, **z}:
        y = 2



x = {0: 1}
match x:
    case {1: 0}:
        y = 0
    case {0: 0}:
        y = 0
    case {}:
        y = 1



x = {0: 1}
match x:
    case {1: 0}:
        y = 0
    case {0: 0}:
        y = 0
    case {**z}:
        y = 1



x = {0: 1}
match x:
    case {1: 0}:
        y = 0
    case {0: 0}:
        y = 0
    case {0: _, **z}:
        y = 1



x = False
match x:
    case bool(z):
        y = 0



x = True
match x:
    case bool(z):
        y = 0



x = bytearray()
match x:
    case bytearray(z):
        y = 0



x = b""
match x:
    case bytes(z):
        y = 0



x = {}
match x:
    case dict(z):
        y = 0



x = 0.0
match x:
    case float(z):
        y = 0



x = frozenset()
match x:
    case frozenset(z):
        y = 0



x = 0
match x:
    case int(z):
        y = 0



x = []
match x:
    case list(z):
        y = 0



x = set()
match x:
    case set(z):
        y = 0



x = ""
match x:
    case str(z):
        y = 0



x = ()
match x:
    case tuple(z):
        y = 0



x = 0
match x,:
    case y,:
        z = 0



w = 0
x = 0
match w, x:
    case y, z:
        v = 0



x = 0
match w := x,:
    case y as v,:
        z = 0



x = 0
y = None
match x:
    case 0 if x:
        y = 0



x = 0
y = None
match x:
    case 1e1000:
        y = 0



x = 0
match x:
    case z:
        y = 0



x = 0
y = None
match x:
    case _ if x:
        y = 0



x = 0
match x:
    case -1e1000:
        y = 0
    case 0:
        y = 1



x = 0
match x:
    case 0 if not x:
        y = 0
    case 1:
        y = 1



x = 0
z = None
match x:
    case 0:
        y = 0
    case z if x:
        y = 1



x = 0
match x:
    case 0:
        y = 0
    case _:
        y = 1



x = 0
match x:
    case 1 if x:
        y = 0
    case 0:
        y = 1



x = 0
y = None
match x:
    case 1:
        y = 0
    case 1 if not x:
        y = 1



x = 0
match x:
    case 1:
        y = 0
    case z:
        y = 1



x = 0
match x:
    case 1 if x:
        y = 0
    case _:
        y = 1



x = 0
match x:
    case z if not z:
        y = 0
    case 0 if x:
        y = 1



x = 0
match x:
    case z if not z:
        y = 0
    case 1:
        y = 1



x = 0
match x:
    case z if not x:
        y = 0
    case z:
        y = 1



x = 0
match x:
    case z if not z:
        y = 0
    case _ if x:
        y = 1



x = 0
match x:
    case _ if not x:
        y = 0
    case 0:
        y = 1



x = 0
y = None
match x:
    case _ if x:
        y = 0
    case 1:
        y = 1



x = 0
z = None
match x:
    case _ if not x:
        y = 0
    case z if not x:
        y = 1



x = 0
match x:
    case _ if not x:
        y = 0
    case _:
        y = 1



match status:
    case 400:
        return "Bad request"
    case 401:
        return "Unauthorized"
    case 403:
        return "Forbidden"
    case 404:
        return "Not found"
    case 418:
        return "I'm a teapot"
    case _:
        return "Something else"



match status:
    case 400:
        return "Bad request"
    case 401 | 403 | 404:
        return "Not allowed"
    case 418:
        return "I'm a teapot"



match point:
    case (0, 0):
        return "Origin"
    case (0, y):
        return f"Y={y}"
    case (x, 0):
        return f"X={x}"
    case (x, y):
        return f"X={x}, Y={y}"
    case _:
        raise ValueError("Not a point")



match point:
    case Point(0, 0):
        return "Origin"
    case Point(0, y):
        return f"Y={y}"
    case Point(x, 0):
        return f"X={x}"
    case Point():
        return "Somewhere else"
    case _:
        return "Not a point"



match point:
    case Point(1, var):
        return var



match point:
    case Point(1, y=var):
        return var



match point:
    case Point(x=1, y=var):
        return var



match point:
    case Point(y=var, x=1):
        return var



match points:
    case []:
        return "No points"
    case [Point(0, 0)]:
        return "The origin"
    case [Point(x, y)]:
        return f"Single point {x}, {y}"
    case [Point(0, y1), Point(0, y2)]:
        return f"Two on the Y axis at {y1}, {y2}"
    case _:
        return "Something else"



match point:
    case Point(x, y) if x == y:
        return f"Y=X at {x}"
    case Point(x, y):
        return "Not on the diagonal"



class Seq(collections.abc.Sequence):
    __getitem__ = None
    def __len__(self):
        return 0
match Seq():
    case []:
        y = 0



class Seq(collections.abc.Sequence):
    __getitem__ = None
    def __len__(self):
        return 42
match Seq():
    case [*_]:
        y = 0



class Seq(collections.abc.Sequence):
    def __getitem__(self, i):
        return i
    def __len__(self):
        return 42
match Seq():
    case [x, *_, y]:
        z = 0



w = range(10)
match w:
    case [x, y, *rest]:
        z = 0


w = range(100)
match w:
    case (x, y, *rest):
        z = 0



w = range(1000)
match w:
    case x, y, *rest:
        z = 0



w = range(1 << 10)
match w:
    case [x, y, *_]:
        z = 0



w = range(1 << 20)
match w:
    case (x, y, *_):
        z = 0



w = range(1 << 30)
match w:
    case x, y, *_:
        z = 0



x = {"bandwidth": 0, "latency": 1}
match x:
    case {"bandwidth": b, "latency": l}:
        y = 0



x = {"bandwidth": 0, "latency": 1, "key": "value"}
match x:
    case {"latency": l, "bandwidth": b}:
        y = 0



x = {"bandwidth": 0, "latency": 1, "key": "value"}
match x:
    case {"bandwidth": b, "latency": l, **rest}:
        y = 0



x = {"bandwidth": 0, "latency": 1}
match x:
    case {"latency": l, "bandwidth": b, **rest}:
        y = 0



w = [Point(-1, 0), Point(1, 2)]
match w:
    case (Point(x1, y1), Point(x2, y2) as p2):
        z = 0



class Color(enum.Enum):
    RED = 0
    GREEN = 1
    BLUE = 2

    match color:
        case Color.RED:
            return "I see red!"
        case Color.GREEN:
            return "Grass is green"
        case Color.BLUE:
            return "I'm feeling the blues :("



class Color(int, enum.Enum):
    RED = 0
    GREEN = 1
    BLUE = 2

    match color:
        case Color.RED:
            return "I see red!"
        case Color.GREEN:
            return "Grass is green"
        case Color.BLUE:
            return "I'm feeling the blues :("



class Class:
    __match_args__ = ("a", "b")
c = Class()
c.a = 0
c.b = 1
match c:
    case Class(x, y):
        z = 0



class Class:
    __match_args__ = ("a", "b")
c = Class()
c.a = 0
c.b = 1
match c:
    case Class(x, b=y):
        z = 0



class Parent:
    __match_args__ = "a", "b"
class Child(Parent):
    __match_args__ = ("c", "d")
c = Child()
c.a = 0
c.b = 1
match c:
    case Parent(x, y):
        z = 0



class Parent:
    __match_args__ = ("a", "b")
class Child(Parent):
    __match_args__ = "c", "d"
c = Child()
c.a = 0
c.b = 1
match c:
    case Parent(x, b=y):
        z = 0



match w:
    case 42:
        out = locals()
        del out["w"]
        return out



match w:
    case 42.0:
        out = locals()
        del out["w"]
        return out



match w:
    case 1 | 2 | 3:
        out = locals()
        del out["w"]
        return out

match w:
    case [1, 2] | [3, 4]:
        out = locals()
        del out["w"]
        return out

match w:
    case x:
        out = locals()
        del out["w"]
        return out

match w:
    case _:
        out = locals()
        del out["w"]
        return out

match w:
    case (x, y, z):
        out = locals()
        del out["w"]
        return out

match w:
    case {"x": x, "y": "y", "z": z}:
        out = locals()
        del out["w"]
        return out

match w:
    case MyClass(int(xx), y="hello"):
        out = locals()
        del out["w"]
        return out

match w:
    case (p, q) as x:
        out = locals()
        del out["w"]
        return out


match 42:
    case 42:
        return locals()

match 1:
    case 1 | 2 | 3:
        return locals()

match ...:
    case _:
        return locals()

match ...:
    case abc:
        return locals()

match ..., ...:
    case a, b:
        return locals()

match {"k": ..., "l": ...}:
    case {"k": a, "l": b}:
        return locals()

match MyClass(..., ...):
    case MyClass(x, y=y):
        return locals()

match ...:
    case b as a:
        return locals()

match x:
    case _:
        return 0

match x:
    case 0:
        return 0

match x:
    case 0:
        return 0
    case _:
        return 1

match x:
    case 0:
        return 0
    case 1:
        return 1

match x:
    case 0:
        return 0
    case 1:
        return 1
    case _:
        return 2

match x:
    case 0:
        return 0
    case 1:
        return 1
    case 2:
        return 2
