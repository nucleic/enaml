# expectations = [
#   { runtime_minimum = [3, 10], runtime_maximum = [3, 11], messages = ["f-string: invalid conversion character: expected 's', 'r', or 'a'"] },
#   { runtime_minimum = [3, 12], runtime_maximum = [3, 15], messages = ["f-string: missing conversion character"], start = [1, 6], end_line = 1, end_offset = 7 }
# ]
# --- source ---
f'{x!}'
