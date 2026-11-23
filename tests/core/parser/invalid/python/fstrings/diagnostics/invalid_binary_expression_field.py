# expectations = [
#   { runtime_minimum = [3, 10], runtime_maximum = [3, 11], messages = ["f-string: invalid syntax"], start = [1, 7], end_line = 1, end_offset = 8 },
#   { runtime_minimum = [3, 12], runtime_maximum = [3, 15], messages = ["f-string: expecting '=', or '!', or ':', or '}'"], start = [1, 11], end_line = 1, end_offset = 12 }
# ]
# --- source ---
f'a = { 1 + }'