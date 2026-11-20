# minimum_python = [3, 12]
# skip_reason = "Type parameters require Python 3.12+"
# start = [1, 11]
# end_line = 1
# end_offset = 16
# messages = ["cannot use bound with ParamSpec"]
# --- source ---
type T[**P: int] = Callable[P, None]