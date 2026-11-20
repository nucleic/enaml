# messages = ["real number required in complex literal"]
# parser_version = [3, 10]
# --- source ---
match x:
    case -1j + 1j:
        pass