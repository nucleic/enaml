# start = [1, 14]
# end_line = 1
# end_offset = 15
# messages = ["var-keyword argument cannot have default value"]
# parser_version = [3, 11]
# --- source ---
def foo(a,**b=3):
	pass