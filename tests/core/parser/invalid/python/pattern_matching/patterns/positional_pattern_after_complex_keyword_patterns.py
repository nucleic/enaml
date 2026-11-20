# start = [2, 16]
# end_line = 2
# end_offset = 17
# messages = ["positional patterns follow keyword patterns"]
# --- source ---
match a:
	case Foo(a=b, c, d=e, f, g=h, i, j=k, ...):
		pass