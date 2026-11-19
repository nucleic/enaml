match w:
    case 1 | 2 | 3:
        out = locals()
        del out["w"]
        return out

match w:
    case [1, 2] | [3, 4]:
        out = locals()
        del out["w"]
        return out

match w:
    case x:
        out = locals()
        del out["w"]
        return out

match w:
    case _:
        out = locals()
        del out["w"]
        return out

match w:
    case (x, y, z):
        out = locals()
        del out["w"]
        return out

match w:
    case {"x": x, "y": "y", "z": z}:
        out = locals()
        del out["w"]
        return out

match w:
    case MyClass(int(xx), y="hello"):
        out = locals()
        del out["w"]
        return out

match w:
    case (p, q) as x:
        out = locals()
        del out["w"]
        return out
