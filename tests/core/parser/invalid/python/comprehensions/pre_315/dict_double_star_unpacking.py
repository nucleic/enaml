# maximum_python = [3, 14]
# skip_reason = "Starred unpacking in comprehensions is valid in Python 3.15+"
# start = [1, 2]
# end_line = 1
# end_offset = 4
# messages = ["dict unpacking cannot be used in dict comprehension"]
# --- source ---
{**a for a in [{1: 2}]}