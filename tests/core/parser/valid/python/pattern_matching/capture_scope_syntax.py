match w:
    case 42:
        out = locals()
        del out["w"]
        return out

match w:
    case 42.0:
        out = locals()
        del out["w"]
        return out
