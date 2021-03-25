def wrap_str_in_stars(text: str) -> str:
    margin = 4
    char = '*'
    top = char * (len(text) + 2 * margin) + '\n'
    text = char + ' ' * (margin - 1) + text + ' ' * (margin - 1) + char
    bottom = '\n' + top
    return top + text + bottom