# minimum_python = [3, 11]
# skip_reason = "Syntax unsupported before 3.11+"
# start = [3, 9]
# end_line = 3
# end_offset = 36
# messages = ["multiple exception types must be parenthesized"]
# --- source ---
try:
	pass
except* ValueError, IndexError as e: