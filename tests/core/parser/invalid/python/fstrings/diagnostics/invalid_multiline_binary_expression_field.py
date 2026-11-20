# expectations = [
#   { runtime_minimum = [3, 10], runtime_maximum = [3, 11], messages = ["f-string: invalid syntax"], start = [3, 7], end_line = 3, end_offset = 8 },
#   { runtime_minimum = [3, 12], runtime_maximum = [3, 15], messages = ["f-string: expecting '=', or '!', or ':', or '}'"], start = [3, 12], end_line = 3, end_offset = 13 }
# ]
# --- source ---
(
	'b'
	f'a = { 1 + }'
)