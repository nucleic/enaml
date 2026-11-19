match status:
    case 400:
        return "Bad request"
    case 401:
        return "Unauthorized"
    case 403:
        return "Forbidden"
    case 404:
        return "Not found"
    case 418:
        return "I'm a teapot"
    case _:
        return "Something else"

match status:
    case 400:
        return "Bad request"
    case 401 | 403 | 404:
        return "Not allowed"
    case 418:
        return "I'm a teapot"

match point:
    case (0, 0):
        return "Origin"
    case (0, y):
        return f"Y={y}"
    case (x, 0):
        return f"X={x}"
    case (x, y):
        return f"X={x}, Y={y}"
    case _:
        raise ValueError("Not a point")

match point:
    case Point(0, 0):
        return "Origin"
    case Point(0, y):
        return f"Y={y}"
    case Point(x, 0):
        return f"X={x}"
    case Point():
        return "Somewhere else"
    case _:
        return "Not a point"

match point:
    case Point(1, var):
        return var

match point:
    case Point(1, y=var):
        return var

match point:
    case Point(x=1, y=var):
        return var

match point:
    case Point(y=var, x=1):
        return var

match points:
    case []:
        return "No points"
    case [Point(0, 0)]:
        return "The origin"
    case [Point(x, y)]:
        return f"Single point {x}, {y}"
    case [Point(0, y1), Point(0, y2)]:
        return f"Two on the Y axis at {y1}, {y2}"
    case _:
        return "Something else"

match point:
    case Point(x, y) if x == y:
        return f"Y=X at {x}"
    case Point(x, y):
        return "Not on the diagonal"
