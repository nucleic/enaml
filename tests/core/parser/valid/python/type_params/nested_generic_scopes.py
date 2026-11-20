class Outer[A]:
    def inner[B](self):
        type TA1[C] = TA1[A, B] | int
        return TA1
