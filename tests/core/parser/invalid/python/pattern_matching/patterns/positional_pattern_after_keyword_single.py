# messages = ["positional patterns follow keyword patterns"]
# start = [2, 14]
# end_line = 2
# end_offset = 15
# --- source ---
match x:
	case A(a=1, 2):
		pass
