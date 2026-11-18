type TA1 = int
type TA2 = TA1 | str



type NonGeneric = int
type Generic[A] = dict[A, A]
type VeryGeneric[T, *Ts, **P] = Callable[P, tuple[T, *Ts]]
type T[X] = X
type T[*P] = Callable[P, None]
type T[**P] = Callable[P, None]
type T[*Ts, **P] = Callable[P, tuple[*Ts]]



type T[X: (int, str)] = tuple[X, ...]



type T[X: int | str] = tuple[X, ...]



def outer[A]():
    type TA1[B] = dict[A, B]
    return TA1



class Parent[A]:
    type TA1[B] = dict[A, B]




class Outer[A]:
    def inner[B](self):
        type TA1[C] = TA1[A, B] | int
        return TA1



def more_generic[T, *Ts, **P]():
    type TA[T2, *Ts2, **P2] = tuple[Callable[P, tuple[T, *Ts]], Callable[P2, tuple[T2, *Ts2]]]
    return TA
