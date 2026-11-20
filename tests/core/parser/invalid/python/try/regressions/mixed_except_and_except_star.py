# messages = ["cannot have both 'except' and 'except*'"]
# parser_version = [3, 11]
# --- source ---
try:
    pass
except* ValueError as e:
    pass
except:
    pass