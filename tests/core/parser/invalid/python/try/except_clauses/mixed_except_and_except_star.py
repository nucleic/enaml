# minimum_python = [3, 11]
# skip_reason = "Syntax unsupported before 3.11+"
# start = [5, 1]
# end_line = 5
# end_offset = 8
# messages = ["cannot have both 'except' and 'except*'"]
# --- source ---
try:
	pass
except ValueError as e:
	pass
except* TypeError:
	pass