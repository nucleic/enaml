# start = [2, 21]
# end_line = 2
# end_offset = 22
# messages = ["positional patterns follow keyword patterns"]
# --- source ---
match a:
	case Foo(z=1, y=2, x):
		pass