def f():
    pass

def f() -> None:
    pass

def f(a):
    pass

def f(a: int) -> Tuple[int, ...]:
    pass

def f(a: int = 1) -> Tuple[int, ...]:
    pass

def f(a, b: int):
    pass

def f(a: bool, b: int = 1):
    pass
