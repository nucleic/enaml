# start = [3, 8]
# end_line = 3
# end_offset = 35
# messages = ["multiple exception types must be parenthesized"]
# --- source ---
try:
	pass
except ValueError, IndexError as e: