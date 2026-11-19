def f(a, *, b):
    pass

def f(a, *, b, c=1):
    pass

def f(a, *, b=1):
    pass

def f(*, b):
    pass

def f(*, b, c=1):
    pass

def f(*, b=1):
    pass
