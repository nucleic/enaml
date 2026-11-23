# start = [2, 12]
# end_line = 2
# end_offset = 13
# messages = ["cannot use '_' as a target"]
# --- source ---
match a:
	case 1 as _:
		pass