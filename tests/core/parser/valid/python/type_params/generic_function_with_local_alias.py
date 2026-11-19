def outer[A]():
    type TA1[B] = dict[A, B]
    return TA1
