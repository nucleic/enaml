# expectations = [
#   { runtime_minimum = [3, 10], runtime_maximum = [3, 13], messages = ["invalid pattern target"], start = [2, 12], end_line = 2, end_offset = 15 },
#   { runtime_minimum = [3, 14], runtime_maximum = [3, 15], messages = ["cannot use expression as pattern target"], start = [2, 12], end_line = 2, end_offset = 15 }
# ]
# --- source ---
match a:
	case 1 as 1+1:
		pass