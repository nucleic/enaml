match 0:
    case 0:
        x = True

match 0:
    case 0 if False:
        x = False
    case 0 if True:
        x = True

match 0:
    case 0:
        x = True
    case 0:
        x = False
