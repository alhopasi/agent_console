def setEmptySpacesLeading(string, length):
    spaces = length - len(string)
    if spaces > 0:
        string = " " * spaces + string
        return string

def setEmptySpacesTrailing(string, length):
    spaces = length - len(string)
    if spaces > 0:
        string += " " * spaces
        return string