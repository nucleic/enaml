# messages = ["Exception groups are"]
# parser_version = [3, 10]
# --- source ---
try:
    a = 1
except *ValueError:
    pass