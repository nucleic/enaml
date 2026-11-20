# messages = ["cannot use '_' as a target"]
# --- source ---
match x:
    case 0:
        pass
    case 1 as _:
        pass