type NonGeneric = int
type Generic[A] = dict[A, A]
type VeryGeneric[T, *Ts, **P] = Callable[P, tuple[T, *Ts]]
type T[X] = X
type T[*P] = Callable[P, None]
type T[**P] = Callable[P, None]
type T[*Ts, **P] = Callable[P, tuple[*Ts]]
