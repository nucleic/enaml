# messages = ["multiple exception types must be parenthesized"]
# parser_version = [3, 13]
# --- source ---
try:
	pass
except ValueError, IndexError:
	pass