# messages = ["multiple exception types must be parenthesized"]
# --- source ---
try:
    pass
except ValueError, IndexError as e: