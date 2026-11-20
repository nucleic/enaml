x = {"bandwidth": 0, "latency": 1}
match x:
    case {"bandwidth": b, "latency": l}:
        y = 0

x = {"bandwidth": 0, "latency": 1, "key": "value"}
match x:
    case {"latency": l, "bandwidth": b}:
        y = 0

x = {"bandwidth": 0, "latency": 1, "key": "value"}
match x:
    case {"bandwidth": b, "latency": l, **rest}:
        y = 0

x = {"bandwidth": 0, "latency": 1}
match x:
    case {"latency": l, "bandwidth": b, **rest}:
        y = 0

w = [Point(-1, 0), Point(1, 2)]
match w:
    case (Point(x1, y1), Point(x2, y2) as p2):
        z = 0
