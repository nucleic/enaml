# start = [2, 12]
# end_line = 2
# end_offset = 13
# messages = ["imaginary number required in complex literal"]
# --- source ---
match x:
	case -1 + 1:
		pass