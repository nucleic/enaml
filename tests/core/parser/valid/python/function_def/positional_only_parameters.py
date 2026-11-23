def f(a, /):
    pass

def f(a=1, /):
    pass

def f(a, b=1, /):
    pass

def f(a, /, b):
    pass

def f(a, c=2, /, b=5):
    pass

def f(a, /, b=1):
    pass
