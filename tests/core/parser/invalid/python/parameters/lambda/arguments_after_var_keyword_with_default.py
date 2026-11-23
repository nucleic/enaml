# start = [1, 22]
# end_line = 1
# end_offset = 23
# messages = ["arguments cannot follow var-keyword argument"]
# parser_version = [3, 11]
# --- source ---
lambda a,*a, b, **c, d=4: None