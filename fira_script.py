'''
The main reader for 'FiraScript'.
'''
import re
from zemia import sql, file
from zemia.common import empty

RESET_DB = True # True to delete fira.db, False to keep it
MAX_RECURSION_DEPTH = 10

class FiraScriptError(Exception):
    '''
    Raised when the syntax of the FiraScript is incorrect.
    '''

class FiraScript:
    '''
    Holds methods to decode FiraScript.
    '''
    def __init__(self, root_word_table: sql.Table, word_table: sql.Table) -> None:
        self.root_word_table = root_word_table
        self.word_table = word_table
        self.silent = True

    def debug(self, command_list: list[str]) -> None:
        '''
        Used for debugging.
        '''
        if empty(command_list):
            raise FiraScriptError(f"DEBUG: No params provided in [{' '.join(command_list)}].")

        if command_list[0] == "SILENT":
            self.silent = not self.silent

    def translate(self, command_list: list[str], **kwargs) -> list[str]:
        '''
        Translates a word.
        '''
         # Kwargs
        silent = kwargs.get("silent", True)

        if not silent:
            print("TRANSLATE", command_list, end=" ... ") # Begin proccessing

        if empty(command_list):
            raise FiraScriptError(f"TRANSLATE: No params provided in [{' '.join(command_list)}].")
        if len(command_list) != 3:
            raise FiraScriptError(f"TRANSLATE: Invalid number of params in [{' '.join(command_list)}].")
        if command_list[1] != "TO" or command_list[2] not in ["e", "f"]:
            raise FiraScriptError(f"TRANSLATE: [{' '.join(command_list)}] not in format '<string> TO <e|f>'.")

        return_list = []
        if command_list[2] == "e":
            root_translation = self.root_word_table.list_record(f"WHERE wordFira = \"{command_list[0]}\"", "wordEng")
            complex_translation = self.word_table.list_record(f"WHERE wordFira = \"{command_list[0]}\"", "wordEng")
        else:
            root_translation = self.root_word_table.list_record(f"WHERE wordEng = \"{command_list[0]}\"", "wordFira")
            complex_translation = self.word_table.list_record(f"WHERE wordEng = \"{command_list[0]}\"", "wordFira")

        if not silent:
            print("DONE") # Proccessing complete

        if len(root_translation)+len(complex_translation) > 0:
            for word in root_translation:
                return_list.append(word[0])
            for word in complex_translation:
                return_list.append(word[0])
        return return_list

    def def_root(self, command_list: list[str], **kwargs) -> dict[str, str]:
        '''
        Defines a root word.
        '''
         # Kwargs
        silent = kwargs.get("silent", True)

        if not silent:
            print("DEFROOT", command_list, end=" ... ") # Begin proccessing

        if empty(command_list):
            raise FiraScriptError(f"DEFROOT: No params provided in [{' '.join(command_list)}].")

        returndict = {"wordEng": command_list[0], "wordFira": command_list[1], "note": ""}

        for i in range(len(command_list)-1, -1, -1):
            if command_list[i] in ["GENDER", "NOTE"]:
                break
        if i == 0:
            raise FiraScriptError(f"DEFROOT: Invalid subcommand in [{' '.join(command_list)}].")
        returndict = self.def_root(command_list[:i]) # Recursion without this subcommand
        if command_list[i] == "GENDER":
            gender_dict = {"m": "Masculine", "f": "Feminine", "n": "Neutral", "p": "Plural"}
            returndict["wordFira"] += self.translate(f"{gender_dict[command_list[i+1]]} TO f")[0]
        elif command_list[i] == "NOTE":
            returndict["note"] = command_list[i+1]

        if not silent:
            print("DONE") # Proccessing complete

        return returndict

    def def_word(self, command_list: list[str], **kwargs) -> None:
        '''
        Defines a word.
        '''
         # Kwargs
        silent = kwargs.get("silent", True)

        if not silent:
            print("DEFWORD", command_list, end=" ... ") # Begin proccessing

        if empty(command_list):
            raise FiraScriptError(f"DEFWORD: No params provided in [{' '.join(command_list)}].")
        if len(command_list) < 3 or command_list[1] != "FROM":
            raise FiraScriptError(f"TRANSLATE: [{' '.join(command_list)}] not in format '<string> FROM <string> <params>'.")

        returndict = {"wordEng": command_list[0], "wordFira": command_list[1], "note": ""}

        for i in range(len(command_list)-1, -1, -1):
            if command_list[i] in ["GENDER", "NOTE"]:
                break
        if i == 0:
            raise FiraScriptError(f"DEFROOT: Invalid subcommand in [{' '.join(command_list)}].")
        returndict = self.def_root(command_list[:i]) # Recursion without this subcommand
        if command_list[i] == "GENDER":
            gender_dict = {"m": "Masculine", "f": "Feminine", "n": "Neutral", "p": "Plural"}
            returndict["wordFira"] += self.translate(f"{gender_dict[command_list[i+1]]} TO f")[0]
        elif command_list[i] == "NOTE":
            returndict["note"] = command_list[i+1]

        if not silent:
            print("DONE") # Proccessing complete

        return returndict


    def list_word(self, command_list: list[str], **kwargs) -> None:
        '''
        Lists all words that match a regex string.
        '''
         # Kwargs
        silent = kwargs.get("silent", True)

        if not silent:
            print("LIST", command_list, end=" ... ") # Begin proccessing

        if empty(command_list):
            raise FiraScriptError(f"LIST: No params provided in [{' '.join(command_list)}].")

        conditions = [f"wordEng = \"{command_list[0]}\" OR wordFira = \"{command_list[0]}\""]
        columns = ["wordEng", "wordFira"]
        tables: list[sql.Table] = [self.root_word_table, self.word_table]
        # Check params
        if len(command_list) == 1:
            # No optional params
            pass
        else:
            while len(command_list) > 1:
                for i in range(len(command_list)-1, -1, -1):
                    if command_list[i] in ["LANG", "TYPE", "NOTE"]:
                        break
                if i == 0:
                    raise FiraScriptError(f"LIST: Invalid subcommand in [{' '.join(command_list)}].")
                if command_list[i] == "LANG":
                    if command_list[i+1] == "e":
                        conditions = [f"wordEng = \"{command_list[0]}\""]
                    elif command_list[i+1] == "f":
                        conditions = [f"wordFira = \"{command_list[0]}\""]
                    else:
                        raise FiraScriptError(f"LIST: Invalid LANG value in [{' '.join(command_list)}].")
                elif command_list[i] == "TYPE":
                    if command_list[i+1] == "r":
                        tables = [self.root_word_table]
                    elif command_list[i+1] == "c":
                        tables = [self.word_table]
                    else:
                        raise FiraScriptError(f"LIST: Invalid TYPE value in [{' '.join(command_list)}].")
                elif command_list[i] == "NOTE":
                    columns.append("note")

                command_list = command_list[:i]

        if not silent:
            print("DONE") # Proccessing complete

        for table in tables:
            for row in table.list_record("WHERE "+" AND ".join(conditions), ", ".join(columns)):
                print(row)


    def help(self, **kwargs) -> list[str]:
        '''
        Prints a list of commands.
        '''
         # Kwargs
        silent = kwargs.get("silent", True)

        if not silent:
            print("HELP", end=" ... ") # Begin proccessing

        f = file.read("fs_info.md", "utf-8")

        if not silent:
            print("DONE") # Proccessing complete

        return ["Info (read from fs_info.md):"]+f

    def read(self, command_list: list[str], depth: int = 0) -> None:
        '''
        Reads a .fira file and executes the contents.
        '''
        if empty(command_list) or len(command_list) != 1:
            raise FiraScriptError(f"READ: Invalid number of params in [{' '.join(command_list)}].")

        if not re.search(".fira$", command_list[0]):
            raise FiraScriptError(f"Invalid file type: [{command_list[0]}].")
        try:
            f = file.read(command_list[0], "utf-8")
        except FileNotFoundError as e:
            raise FiraScriptError(f"File not found: [{command_list[0]}].") from e
        for line_number, file_line in enumerate(f):
            try:
                self.decode_input(file_line, depth=depth+1)
            except FiraScriptError as e:
                raise FiraScriptError(f"Error in file [{command_list[0]}] at line {line_number+1}: {e}.") from e

    def decode_input(self, line: str, **kwargs) -> None:
        '''
        Reads a line of FiraScript.
        '''
         # Kwargs
        depth = kwargs.get("depth", 0)
        if depth > MAX_RECURSION_DEPTH:
            raise FiraScriptError(f"Max recursion depth ({MAX_RECURSION_DEPTH}) reached.")

        command_list = line.split(" ")
        for i, command in enumerate(command_list):
            if command == "": # Skip empty commands
                continue
            if re.search('^"', command) is not None: # Check if the command is a String
                if re.search('"$', command) is None: # Check if the command is the start of a multi-word String
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
                # Remove the quotes
                command_list[i] = command_list[i][1:-1]
        if command_list[0] == "":
            pass
        elif command_list[0] == "HELP":
            for i in self.help(silent=self.silent):
                print(i)
        elif command_list[0] == "READ":
            self.read(command_list[1:], depth)
        elif command_list[0] == "DEFROOT":
            word_eng, word_fira = self.def_root(command_list[1:], silent=self.silent)
            self.root_word_table.add_record('"'+word_eng+'"', '"'+word_fira+'"', "\"\"")
        elif command_list[0] == "DEFWORD":
            self.def_word(command_list[1:], silent=self.silent)
        elif command_list[0] == "LIST":
            self.list_word(command_list[1:], silent=self.silent)
        elif command_list[0] == "TRANSLATE":
            for word in self.translate(command_list[1:], silent=self.silent):
                print(word, end=" ")
            print()
        else:
            raise FiraScriptError(f"Invalid command: [{command_list[0]}].")

def main() -> None:
    '''Main function.'''
    if RESET_DB:
        file.delete("fira.db")
     # Set up db connection
    sql_connection = sql.connect(f"fira.db")
    root_word_table = sql.Table(
        sql_connection,
        "rootWordTable", 
        ["wordEng STRING NOT NULL", "wordFira STRING NOT NULL", "note STRING", "PRIMARY KEY (wordEng, wordFira)"]
    )
    word_table = sql.Table(
            sql_connection,
            "wordTable",
            ["wordEng STRING NOT NULL", "wordFira STRING NOT NULL", "formula STRING NOT NULL", "note STRING", "PRIMARY KEY (wordEng, wordFira)"]
    )
     # Create FiraScript object
    fira = FiraScript(root_word_table, word_table)
     # Read input
    print("Enter FiraScript commands. Type 'HELP' for commands.")
    while True:
        user_inp = input("> ")
        if user_inp == "EXIT":
            break
        try:
            fira.decode_input(user_inp)
        except FiraScriptError as e:
            print(e)

main()
