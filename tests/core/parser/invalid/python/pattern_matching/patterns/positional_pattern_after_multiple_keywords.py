# start = [2, 24]
# end_line = 2
# end_offset = 25
# messages = ["positional patterns follow keyword patterns"]
# --- source ---
match a:
	case Foo(a, z=1, y=2, x):
		pass