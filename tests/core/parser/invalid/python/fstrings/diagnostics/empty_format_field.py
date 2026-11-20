# expectations = [
#   { runtime_minimum = [3, 10], runtime_maximum = [3, 10], messages = ["f-string: empty expression not allowed"] },
#   { runtime_minimum = [3, 11], runtime_maximum = [3, 11], messages = ["expression required before ':'"] },
#   { runtime_minimum = [3, 12], runtime_maximum = [3, 15], messages = ["expression required before ':'"], start = [1, 8], end_line = 1, end_offset = 9 }
# ]
# --- source ---
f'a = {:}'