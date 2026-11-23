# expectations = [
#   { runtime_minimum = [3, 10], runtime_maximum = [3, 11], messages = ["iterable argument unpacking follows keyword argument unpacking"] },
#   { runtime_minimum = [3, 12], runtime_maximum = [3, 15], messages = ["iterable argument unpacking follows keyword argument unpacking"], start = [1, 6], end_line = 1, end_offset = 10 }
# ]
# --- source ---
f(**a, *b)