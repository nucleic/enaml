# minimum_python = [3, 11]
# skip_reason = "Syntax only permitted on 3.11+"
# start = [4, 1]
# end_line = 4
# end_offset = 5
# messages = ["expected an indented block after 'except*' statement on line 3"]
# --- source ---
try:
	pass
except* Exception as e:
pass