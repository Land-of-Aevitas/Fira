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
            print(f"Silent mode set to {self.silent}.")

    def translate(self, command_list: list[str], **kwargs) -> dict[str, list[str]]:
        '''
        Translates a word.
        '''
         # Kwargs
        silent = kwargs.get("silent", True)

        func_name = "TRANSLATE"
        if not silent:
            print(func_name, command_list, end=" ... ") # Begin proccessing

        if empty(command_list):
            raise FiraScriptError(f"{func_name}: No params provided in [{' '.join(command_list)}].")
        if len(command_list) < 3:
            raise FiraScriptError(f"{func_name}: Invalid number of params in [{' '.join(command_list)}].")

        return_dict: dict[str, list[str]] = {"words": []}

        root_translation, complex_translation = [], []
        if command_list[1] == "TO":
            if str.lower(command_list[2]) in ["e", "english"]:
                root_translation = self.root_word_table.list_record(f"WHERE wordFira = \"{command_list[0]}\"", "wordEng")
                complex_translation = self.word_table.list_record(f"WHERE wordFira = \"{command_list[0]}\"", "wordEng")
            elif str.lower(command_list[2]) in ["f", "fira"]:
                root_translation = self.root_word_table.list_record(f"WHERE wordEng = \"{command_list[0]}\"", "wordFira")
                complex_translation = self.word_table.list_record(f"WHERE wordEng = \"{command_list[0]}\"", "wordFira")
            else:
                raise FiraScriptError(f"{func_name}: [{' '.join(command_list)}] not in format '<string> TO <e|f>', missing <e|f>.")
        else:
            raise FiraScriptError(f"{func_name}: [{' '.join(command_list)}] not in format '<string> TO <e|f>', missing TO.")

        if len(root_translation)+len(complex_translation) > 0:
            for word in root_translation:
                return_dict["words"].append(word[0])
            for word in complex_translation:
                return_dict["words"].append(word[0])

        if not silent:
            print("DONE") # Proccessing complete
        return return_dict

    def def_root(self, command_list: list[str], **kwargs) -> dict[str, str]:
        '''
        Defines a root word.
        '''
         # Kwargs
        silent = kwargs.get("silent", True)

        func_name = "DEFROOT"
        if not silent:
            print(func_name, command_list, end=" ... ") # Begin proccessing

        if empty(command_list):
            raise FiraScriptError(f"{func_name}: No params provided in [{' '.join(command_list)}].")

        returndict = {"wordEng": command_list[0], "wordFira": command_list[1], "note": ""}

        if len(command_list) > 2:
            for i in range(len(command_list)-1, -1, -1):
                if command_list[i] in ["GENDER", "NOTE"]:
                    break
            if i == 0:
                raise FiraScriptError(f"{func_name}: Invalid subcommand in [{' '.join(command_list)}].")
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

        func_name = "DEFWORD"
        if not silent:
            print(func_name, command_list, end=" ... ") # Begin proccessing

        if empty(command_list):
            raise FiraScriptError(f"{func_name}: No params provided in [{' '.join(command_list)}].")
        if len(command_list) < 3 or command_list[1] != "FROM":
            raise FiraScriptError(f"{func_name}: [{' '.join(command_list)}] not in format '<string> FROM <string> <params>'.")

        returndict = {"wordEng": command_list[0], "wordFira": command_list[1], "note": ""}
        with_type = ""

        for i in range(len(command_list)-1, -1, -1):
            if command_list[i] in ["WITH-SLICE", "GENDER", "NOTE"]:
                break
        if i != 0:
            if command_list[i] == "WITH-SLICE":
                with_type = "SLICE"
            else:
                returndict = self.def_word(command_list[:i]) # Recursion without this subcommand
                if command_list[i] == "GENDER":
                    gender_dict = {"m": "Masculine", "f": "Feminine", "n": "Neutral", "p": "Plural"}
                    returndict["wordFira"] += self.translate(f"{gender_dict[command_list[i+1]]} TO f")[0]
                elif command_list[i] == "NOTE":
                    returndict["note"] = command_list[i+1]

         # Get words
        

        if not silent:
            print("DONE") # Proccessing complete

        return returndict

    def list_word(self, command_list: list[str], **kwargs) -> None:
        '''
        Lists all words that match a regex string.
        '''
         # Kwargs
        silent = kwargs.get("silent", True)

        func_name = "LIST"
        if not silent:
            print(func_name, command_list, end=" ... ") # Begin proccessing

        if empty(command_list):
            raise FiraScriptError(f"{func_name}: No params provided in [{' '.join(command_list)}].")

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
                    raise FiraScriptError(f"{func_name}: Invalid subcommand in [{' '.join(command_list)}].")
                if command_list[i] == "LANG":
                    if command_list[i+1] == "e":
                        conditions = [f"wordEng = \"{command_list[0]}\""]
                    elif command_list[i+1] == "f":
                        conditions = [f"wordFira = \"{command_list[0]}\""]
                    else:
                        raise FiraScriptError(f"{func_name}: Invalid LANG value in [{' '.join(command_list)}].")
                elif command_list[i] == "TYPE":
                    if command_list[i+1] == "r":
                        tables = [self.root_word_table]
                    elif command_list[i+1] == "c":
                        tables = [self.word_table]
                    else:
                        raise FiraScriptError(f"{func_name}: Invalid TYPE value in [{' '.join(command_list)}].")
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

        func_name = "HELP"
        if not silent:
            print(func_name, end=" ... ") # Begin proccessing

        f = file.read("fs_info.md", "utf-8")

        if not silent:
            print("DONE") # Proccessing complete

        return ["Info (read from fs_info.md):"]+f

    def read(self, command_list: list[str], depth: int = 0) -> bool:
        '''
        Reads a .fira file and executes the contents.
        '''
        func_name = "READ"
        if empty(command_list) or len(command_list) != 1:
            raise FiraScriptError(f"{func_name}: Invalid number of params in [{' '.join(command_list)}].")

        if not re.search(".fira$", command_list[0]):
            raise FiraScriptError(f"{func_name}: Invalid file type: [{command_list[0]}].")
        try:
            f = file.read(command_list[0], "utf-8")
        except FileNotFoundError as e:
            raise FiraScriptError(f"{func_name}: File not found: [{command_list[0]}].") from e
        for line_number, file_line in enumerate(f):
            try:
                end = self.decode_input(file_line, depth=depth+1)
                if end:
                    return True
            except FiraScriptError as e:
                raise FiraScriptError(f"{func_name}: Error in file [{command_list[0]}] at line {line_number+1}: {e}") from e
        return False

    def decode_input(self, line: str, **kwargs) -> bool:
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
        elif command_list[0] == "EXIT":
            return True
        elif command_list[0] == "DEBUG":
            self.debug(command_list[1:])
        elif command_list[0] == "HELP":
            for i in self.help(silent=self.silent):
                print(i)
        elif command_list[0] == "READ":
            return self.read(command_list[1:], depth)
        elif command_list[0] == "DEFROOT":
            defroot_dict = self.def_root(command_list[1:], silent=self.silent)
            self.root_word_table.add_record(
                "\""+defroot_dict["wordEng"]+"\"", 
                "\""+defroot_dict["wordFira"]+"\"", 
                "\""+defroot_dict["note"]+"\"")
        elif command_list[0] == "DEFWORD":
            self.def_word(command_list[1:], silent=self.silent)
        elif command_list[0] == "LIST":
            self.list_word(command_list[1:], silent=self.silent)
        elif command_list[0] == "TRANSLATE":
            translate_dict = self.translate(command_list[1:], silent=self.silent)
            for word in translate_dict["words"]:
                print(word, end=" ")
            print()
        else:
            raise FiraScriptError(f"Invalid command: [{command_list[0]}].")
        return False

def main() -> None:
    '''Main function.'''
    if RESET_DB:
        file.delete("fira.db")
     # Set up db connection
    sql_connection = sql.connect(f"fira.db")
    root_word_table = sql.Table(
        sql_connection,
        "rootWordTable", 
        [
            "wordEng STRING NOT NULL", 
            "wordFira STRING NOT NULL", 
            "note STRING", 
            "PRIMARY KEY (wordEng, wordFira)"
        ]
    )
    word_table = sql.Table(
            sql_connection,
            "wordTable",
            [
                "wordEng STRING NOT NULL", 
                "wordFira STRING NOT NULL", 
                "formula STRING NOT NULL", 
                "note STRING", 
                "PRIMARY KEY (wordEng, wordFira)"
            ]
    )
     # Create FiraScript object
    fira = FiraScript(root_word_table, word_table)
     # Read input
    print("Enter FiraScript. Type 'HELP' for commands.")
    end = False
    while not end:
        user_inp = input("> ")
        try:
            end = fira.decode_input(user_inp)
        except FiraScriptError as e:
            print(e)

main()
