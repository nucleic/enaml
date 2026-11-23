# start = [1, 23]
# end_line = 1
# end_offset = 25
# messages = ["arguments cannot follow var-keyword argument"]
# parser_version = [3, 11]
# --- source ---
def foo(a,*a, b, **c, **d):
	pass