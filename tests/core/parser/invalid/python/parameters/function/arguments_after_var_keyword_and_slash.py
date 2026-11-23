# start = [1, 19]
# end_line = 1
# end_offset = 20
# messages = ["arguments cannot follow var-keyword argument"]
# parser_version = [3, 11]
# --- source ---
def foo(a=1,/,**b,/,c):
	pass