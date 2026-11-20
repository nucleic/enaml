# start = [1, 13]
# end_line = 1
# end_offset = 14
# messages = ["var-positional argument cannot have default value"]
# parser_version = [3, 11]
# --- source ---
def foo(a,*b=3,c):
	pass