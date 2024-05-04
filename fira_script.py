'''
The main reader for 'FiraScript'.
'''
import re
from zemia import sql, file

RESET_DB = True # True to delete fira.db, False to keep it

class RootWordTable(sql.Table):
    '''Initialises the WordTable, which stores all words that have been defined so far, along with the formulas to define them.'''
    def __init__(self, connection: sql.Connection) -> None:
        super().__init__(
            connection,
            "rootWordTable",
            ["id INTEGER NOT NULL UNIQUE", "wordEng STRING NOT NULL", "wordFira STRING NOT NULL", "note STRING", "PRIMARY KEY (id)"]
        )

class WordTable(sql.Table):
    '''Initialises the WordTable, which stores all words that have been defined so far, along with the formulas to define them.'''
    def __init__(self, connection: sql.Connection) -> None:
        super().__init__(
            connection,
            "wordTable",
            ["id INTEGER NOT NULL UNIQUE", "wordEng STRING NOT NULL", "wordFira STRING NOT NULL", "formula STRING NOT NULL", "note STRING", "PRIMARY KEY (id)"]
        )

class FiraScript:
    '''
    Holds methods to decode FiraScript.
    '''
    def __init__(self, root_word_table: RootWordTable, word_table: WordTable) -> None:
        self.root_word_table = root_word_table
        self.word_table = word_table

    def defroot(self, command_list: list[str]) -> None:
        '''
        Defines a root word.
        '''
        print("DEFROOT", command_list)

        record_id = self.root_word_table.list_record(columns="COUNT(*)")[0][0] + 1
        self.root_word_table.add_record(record_id, command_list[0], command_list[1])

    def defword(self, command_list: list[str]) -> None:
        '''
        Defines a word.
        '''
        print("DEFWORD", command_list)

    def listword(self, command_list: list[str]) -> None:
        '''
        Lists all words that match a regex string.
        '''
        # Check params
        if len(command_list) == 1:
            # No params
            print(self.word_table.list_record(command_list[0]))

    def help(self) -> None:
        '''
        Prints a list of commands.
        '''
        print("Commands (read from fs_info.md):")
        for line in file.read("fs_info.md", "utf-8"):
            print(line)

    def decode_input(self, line: str) -> None:
        '''
        Reads a line of FiraScript.
        '''
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
        if command_list[0] == "":
            pass
        elif command_list[0] == "HELP":
            self.help()
        elif command_list[0] == "EXIT":
            pass
        elif command_list[0] == "READ":
            if not re.search(".fira$", command_list[1]):
                raise ValueError(f"Invalid file type: {command_list[1]}.")
            try:
                f = file.read(command_list[1], "utf-8")
            except FileNotFoundError as e:
                raise FileNotFoundError(f"File not found: {command_list[1]}.") from e
            for file_line in f:
                self.decode_input(file_line)
        elif command_list[0] == "DEFROOT":
            self.defroot(command_list[1:])
        elif command_list[0] == "DEFWORD":
            self.defword(command_list[1:])
        else:
            raise ValueError(f"Invalid command: {command_list[0]}.")

def main() -> None:
    '''Main function.'''
    if RESET_DB:
        file.delete("fira.db")
     # Set up db connection
    sql_connection = sql.connect(f"fira.db")
    root_word_table = RootWordTable(sql_connection)
    word_table = WordTable(sql_connection)
     # Create FiraScript object
    fira = FiraScript(root_word_table, word_table)
     # Read input
    print("Enter FiraScript commands. Type 'HELP' for commands.")
    while True:
        user_inp = input("> ")
        if user_inp == "EXIT":
            break
        fira.decode_input(user_inp)

main()
