# start = [6, 1]
# end_line = 6
# end_offset = 5
# messages = ["expected an indented block after 'finally' statement on line 5"]
# --- source ---
try:
	pass
except Exception:
	pass
finally:
pass