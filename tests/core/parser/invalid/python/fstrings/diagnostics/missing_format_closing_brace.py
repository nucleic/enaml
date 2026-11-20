# expectations = [
#   { runtime_minimum = [3, 10], runtime_maximum = [3, 11], messages = ["f-string: expecting '}'"] },
#   { runtime_minimum = [3, 12], runtime_maximum = [3, 15], messages = ["f-string: expecting '}', or format specs"], start = [1, 9], end_line = 1, end_offset = 10 }
# ]
# --- source ---
f'{x:{y}'
