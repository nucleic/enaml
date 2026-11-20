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
