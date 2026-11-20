# expectations = [
#   { runtime_minimum = [3, 10], runtime_maximum = [3, 11], messages = ["f-string: expression required before '='"] },
#   { runtime_minimum = [3, 12], runtime_maximum = [3, 15], messages = ["f-string: valid expression required before '='"], start = [1, 4], end_line = 1, end_offset = 5 }
# ]
# --- source ---
f'{=}'
