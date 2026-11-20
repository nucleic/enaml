# start = [1, 18]
# end_line = 1
# end_offset = 19
# messages = ["var-positional argument cannot have default value"]
# parser_version = [3, 11]
# --- source ---
def foo(a,*b: int=,c):
	pass