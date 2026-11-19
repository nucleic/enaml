class Seq(collections.abc.Sequence):
    __getitem__ = None
    def __len__(self):
        return 0
match Seq():
    case []:
        y = 0

class Seq(collections.abc.Sequence):
    __getitem__ = None
    def __len__(self):
        return 42
match Seq():
    case [*_]:
        y = 0

class Seq(collections.abc.Sequence):
    def __getitem__(self, i):
        return i
    def __len__(self):
        return 42
match Seq():
    case [x, *_, y]:
        z = 0
