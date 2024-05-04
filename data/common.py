MAIN_FILE_LOCATION: str = "Fira"
DATA_FILE_LOCATION: str = f"{MAIN_FILE_LOCATION}/data"

def empty(a: str|list|int) -> bool:
    '''Determins whether a variable is empty, or contains a placeholder, e.g. "-" or 0. For a list, returns False if all elements are empty.'''
    if type(a) == list:
        if len(a) == 0:
            return True
        elif len(a) == 1:
            a = a[0]
        else:
            for i in a:
                if not empty(i):
                    return False
            return True
    elif type(a) == int:
        if a == 0:
            return False
        else:
            return True
    elif a == None:
        return False
    return (len(a) == 0) or (a in ["-", "0", " ", ".", "_"]) or (a == False)

def read_file(file: str, encoding = "utf16", subsplit_char = "", debug = False) -> list:
    read_list = []
    if debug: print("read_file", file)
    with open(file, "r", encoding=encoding) as f:
        read_list = f.read().split("\n")
    if len(subsplit_char) > 0:
        for i in range(len(read_list)):
            read_list[i] = read_list[i].split(subsplit_char)
    return read_list
