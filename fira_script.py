'''
The main reader for 'FiraScript'.
'''
import re
from zemia import sql

class RootWordTable(sql.Table):
    '''Initialises the WordTable, which stores all words that have been defined so far, along with the formulas to define them.'''
    def __init__(self, connection: sql.Connection) -> None:
        super().__init__(
            connection,
            "rootWordTable",
            ["id INTEGER NOT NULL", "wordEng STRING NOT NULL", "formula STRING NOT NULL", "PRIMARY KEY (id)"]
        )

class WordTable(sql.Table):
    '''Initialises the WordTable, which stores all words that have been defined so far, along with the formulas to define them.'''
    def __init__(self, connection: sql.Connection) -> None:
        super().__init__(
            connection,
            "wordTable",
            ["id INTEGER NOT NULL", "wordEng STRING NOT NULL", "wordFira STRING NOT NULL", "PRIMARY KEY (id)"]
        )

def read_file(filename: str) -> list[str]:
    '''Reads the file and returns its content as a list of strings.'''
    with open(filename, "r", encoding="utf-8") as f:
        return f.read().splitlines()



def main() -> None:
    '''Main function.'''
    #sql_connection = sql.connect(f"{FILE_LOC}/fira.db")
    #root_word_table = RootWordTable(sql_connection)

    user_inp = read_file("test.fira")
    for line in user_inp:
        command_list = line.split(" ")
        for i, command in enumerate(command_list):
            if command == "": # Skip empty commands
                continue
            if re.search('^"', command) is not None and re.search('"$', command) is None: # Check if the command is the start of a multi-word String
                merge_end = -1
                # Find the end of the string
                for j in range(i+1, len(command_list)):
                    if re.search('"$', command_list[j]):
                        merge_end = j
                        break
                # Merge the string
                for k in range(i+1, merge_end+1):
                    command_list[i] += f" {command_list[k]}"
                # Remove other parts from the list
                for _ in range(merge_end-i):
                    command_list.pop(i+1)
            print(command, end=" ")
        print()

main()
