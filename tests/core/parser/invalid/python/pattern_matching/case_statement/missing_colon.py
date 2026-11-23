# expectations = [
#   { runtime_minimum = [3, 10], runtime_maximum = [3, 11], messages = ["expected ':'"], start = [2, 8], end_line = 2, end_offset = 8 },
#   { runtime_minimum = [3, 12], runtime_maximum = [3, 15], messages = ["expected ':'"], start = [2, 8], end_line = 2, end_offset = 9 }
# ]
# --- source ---
match a:
	case 1
		pass