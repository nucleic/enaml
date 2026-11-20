# expectations = [
#   { runtime_minimum = [3, 10], runtime_maximum = [3, 11], messages = ["f-string: expecting '}'"] },
#   { runtime_minimum = [3, 12], runtime_maximum = [3, 15], messages = ["expecting '!', or ':', or '}'"], start = [1, 10], end_line = 1, end_offset = 11 }
# ]
# --- source ---
f'a = {a=d}'