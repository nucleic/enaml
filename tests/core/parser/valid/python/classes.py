class A:
    pass


class A(B):
    pass


class A(
    B,
    C,
):
    pass


class A(metaclass=M):
    pass


class A(B, metaclass=M):
    pass


class A(*t):
    pass


class A(B, *t):
    pass


class A(**kw):
    pass


class A(B, **kw):
    pass
