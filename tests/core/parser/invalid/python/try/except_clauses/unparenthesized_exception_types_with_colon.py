# maximum_python = [3, 13]
# skip_reason = "PEP 758 allows unparenthesized except and except* blocks"
# start = [3, 8]
# end_line = 3
# end_offset = 30
# messages = ["multiple exception types must be parenthesized"]
# --- source ---
try:
	pass
except ValueError, IndexError: