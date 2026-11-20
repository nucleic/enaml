# expectations = [
#   { runtime_minimum = [3, 10], runtime_maximum = [3, 13], messages = ["invalid syntax"], start = [3, 18], end_line = 3, end_offset = 19 },
#   { runtime_minimum = [3, 14], runtime_maximum = [3, 15], messages = ["invalid syntax"], start = [3, 33], end_line = 3, end_offset = 34 }
# ]
# --- source ---
try:
	pass
except ValueError, IndexError, a=1: