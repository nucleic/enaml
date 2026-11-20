# start = [1, 22]
# end_line = 1
# end_offset = 23
# messages = ["* argument may appear only once"]
# parser_version = [3, 11]
# --- source ---
def foo(a,b,/,c,*b,c,*d,**e):
	pass