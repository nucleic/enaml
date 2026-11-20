try:
    pass
finally:
    pass

try:
    pass
except:
    raise
finally:
    pass

try:
    pass
except ValueError:
    pass
except (IndexError, RuntimeError,):
    pass
except Exception as e:
    pass
else:
    pass
finally:
    pass
