def more_generic[T, *Ts, **P]():
    type TA[T2, *Ts2, **P2] = tuple[Callable[P, tuple[T, *Ts]], Callable[P2, tuple[T2, *Ts2]]]
    return TA
