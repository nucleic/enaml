def f(b=1, *c):
    pass

def f(*args):
    pass

def f(*args: *Ts, option=1):
    pass

def f(*args: *Ts):
    pass

def f(**kwargs):
    pass

def f(a, **kwargs):
    pass

def f(a=1, **kwargs):
    pass

def f(*, a=1, **kwargs):
    pass

def f(*a, **b):
    pass

def f(a, /, b, *, v=1, **d):
    pass
