# expectations = [
#   { runtime_minimum = [3, 10], runtime_maximum = [3, 11], messages = ["expected ':'"], start = [3, 22], end_line = 3, end_offset = 22 },
#   { runtime_minimum = [3, 12], runtime_maximum = [3, 15], messages = ["expected ':'"], start = [3, 22], end_line = 3, end_offset = 23 }
# ]
# --- source ---
try:
	pass
except Exception as e
pass