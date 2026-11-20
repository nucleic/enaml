# start = [1, 15]
# end_line = 1
# end_offset = 16
# messages = ["parameter without a default follows parameter with a default"]
# parser_version = [3, 12]
# --- source ---
def f(a=1, /, b):
	pass