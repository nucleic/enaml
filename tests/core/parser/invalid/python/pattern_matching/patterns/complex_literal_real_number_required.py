# start = [2, 8]
# end_line = 2
# end_offset = 10
# messages = ["real number required in complex literal"]
# --- source ---
match x:
	case -1j + 1j:
		pass