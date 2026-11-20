# messages = ["positional patterns follow keyword patterns"]
# parser_version = [3, 10]
# --- source ---
match a:
    case Foo(z=1, y=2, x):
        pass