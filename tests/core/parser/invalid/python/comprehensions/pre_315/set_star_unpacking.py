# maximum_python = [3, 14]
# skip_reason = "Starred unpacking in comprehensions is valid in Python 3.15+"
# start = [1, 2]
# end_line = 1
# end_offset = 4
# messages = ["iterable unpacking cannot be used in comprehension"]
# --- source ---
{*a for a in enumerate(range(5))}