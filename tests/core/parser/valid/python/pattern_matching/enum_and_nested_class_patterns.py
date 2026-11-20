class Color(enum.Enum):
    RED = 0
    GREEN = 1
    BLUE = 2

    match color:
        case Color.RED:
            return "I see red!"
        case Color.GREEN:
            return "Grass is green"
        case Color.BLUE:
            return "I'm feeling the blues :("

class Color(int, enum.Enum):
    RED = 0
    GREEN = 1
    BLUE = 2

    match color:
        case Color.RED:
            return "I see red!"
        case Color.GREEN:
            return "Grass is green"
        case Color.BLUE:
            return "I'm feeling the blues :("
