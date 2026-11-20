# start = [1, 16]
# end_line = 1
# end_offset = 17
# messages = ["* argument may appear only once"]
# parser_version = [3, 11]
# --- source ---
def foo(a,*b,c,*d,*e,c):
	pass