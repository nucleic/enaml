# minimum_python = [3, 12]
# skip_reason = "Type parameters require Python 3.12+"
# start = [1, 10]
# end_line = 1
# end_offset = 22
# messages = ["cannot use constraints with TypeVarTuple"]
# --- source ---
type T[*P: (int, str)] = Callable[P, None]