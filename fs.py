'''
The main reader for 'FiraScript'.
'''
 # Library imports
import re
from zemia import sql, file
from zemia.common import empty, Colours
 # Local imports
from fs_errors import FSError, FSSyntaxError, FSRecursionError

class FiraScript:
    '''Methods to decode FiraScript.'''
    def __init__(self, root_word_table: sql.Table, word_table: sql.Table) -> None:
        self.root_word_table = root_word_table
        self.word_table = word_table
        self.silent = True
        self.max_recursion_depth = 10

    def debug(self, command_list: list[str]) -> None:
        '''Used for debugging.'''
        func_name = "DEBUG"
        if empty(command_list):
            raise FSSyntaxError(f"{func_name} ERROR: No params provided in 「{' '.join(command_list)}」.")

        for i in range(len(command_list)-1, -1, -1):
            if command_list[i] in ["SILENT", "MAX-RECUR"]:
                break
        if i > 0:
            self.debug(command_list[:i]) # Recursion without this subcommand
        if command_list[i] == "SILENT":
            if i == len(command_list)-1: # No param
                self.silent = not self.silent
            else:
                if command_list[i+1].lower() in ["true", "t", "1"]:
                    self.silent = True
                elif command_list[i+1].lower() in ["false", "f", "0"]:
                    self.silent = False
                else:
                    raise FSSyntaxError(f"{func_name} ERROR: Invalid SILENT value in 「{' '.join(command_list)}」.")
            print(f"Silent mode set to {self.silent}.")
        elif command_list[i] == "MAX-RECUR":
            old_max = self.max_recursion_depth
            if i == len(command_list)-1: # No param
                self.max_recursion_depth = 10
            else:
                try:
                    self.max_recursion_depth = int(command_list[i+1])
                except ValueError as e:
                    raise FSSyntaxError(f"{func_name} ERROR: Invalid MAX-RECUR value in 「{' '.join(command_list)}」.") from e
            print(f"Max recursion depth updated from {old_max} to {self.max_recursion_depth}.")
        else:
            raise FSSyntaxError(f"{func_name} ERROR: Invalid subcommand in 「{' '.join(command_list)}」.")

    def translate(self, command_list: list[str], **kwargs) -> str:
        '''Translates a word.'''
         # Kwargs
        silent = kwargs.get("silent", True)

        func_name = "TRANSLATE"
        if not silent:
            print(func_name, command_list, end=" ... ") # Begin proccessing

        if empty(command_list):
            raise FSSyntaxError(f"{func_name} ERROR: No params provided in 「{' '.join(command_list)}」.")
        if len(command_list) < 3:
            raise FSSyntaxError(f"{func_name} ERROR: Invalid number of params in 「{' '.join(command_list)}」.")

        #return_dict: dict[str, list[str]] = {"words": []}

        root_translation, complex_translation = [], []
        if command_list[1] == "TO":
            if str.lower(command_list[2]) in ["e", "english"]:
                root_translation = self.root_word_table.list_record(f"WHERE wordFira = \"{command_list[0].lower()}\"", "wordEng")
                complex_translation = self.word_table.list_record(f"WHERE wordFira = \"{command_list[0].lower()}\"", "wordEng")
            elif str.lower(command_list[2]) in ["f", "fira"]:
                root_translation = self.root_word_table.list_record(f"WHERE wordEng = \"{command_list[0].lower()}\"", "wordFira")
                complex_translation = self.word_table.list_record(f"WHERE wordEng = \"{command_list[0].lower()}\"", "wordFira")
            else:
                raise FSSyntaxError(f"{func_name} ERROR: 「{' '.join(command_list)}」 not in format '<string> TO <e|f>', missing <e|f>.")
        else:
            raise FSSyntaxError(f"{func_name} ERROR: 「{' '.join(command_list)}」 not in format '<string> TO <e|f>', missing TO.")

        if not silent:
            print("DONE") # Proccessing complete

        if len(root_translation) > 0:
            return root_translation[0][0]
        if len(complex_translation) > 0:
            return complex_translation[0][0]

        raise FSSyntaxError(f"{func_name} ERROR: No translation found for 「{' '.join(command_list)}」.")

    def def_root(self, command_list: list[str], **kwargs) -> dict[str, str]:
        '''Defines a root word.'''
         # Kwargs
        silent = kwargs.get("silent", True)

        func_name = "DEFROOT"
        if not silent:
            print(func_name, command_list, end=" ... ") # Begin proccessing

        if empty(command_list):
            raise FSSyntaxError(f"{func_name} ERROR: No params provided in 「{' '.join(command_list)}」.")

        returndict = {"wordEng": command_list[0], "wordFira": command_list[1], "note": ""}

        if len(command_list) > 2:
            for i in range(len(command_list)-1, -1, -1):
                if command_list[i] in ["GENDER", "NOTE"]:
                    break
            if i == 0:
                raise FSSyntaxError(f"{func_name} ERROR: Invalid subcommand in 「{' '.join(command_list)}」.")
            returndict = self.def_root(command_list[:i]) # Recursion without this subcommand
            if command_list[i] == "GENDER":
                gender_dict = {"m": "Masculine", "f": "Feminine", "n": "Neutral", "p": "Plural"}
                returndict["wordFira"] += self.translate(f"{gender_dict[command_list[i+1]]} TO f")
            elif command_list[i] == "NOTE":
                returndict["note"] = command_list[i+1]

        if not silent:
            print("DONE") # Proccessing complete

        return returndict

    def def_word(self, command_list: list[str], **kwargs) -> None:
        '''Defines a word.'''
         # Kwargs
        silent = kwargs.get("silent", True)
        iteration = kwargs.get("iteration", False) # Whether this is an iteration of def_word and so should not apply WITH subcommands

        func_name = "DEFWORD"
        if not silent:
            print(func_name, command_list, end=" ... ") # Begin proccessing

        if empty(command_list):
            raise FSSyntaxError(f"{func_name} ERROR: No params provided in 「{' '.join(command_list)}」.")
        if len(command_list) < 3 or command_list[1] != "FROM":
            raise FSSyntaxError(f"{func_name} ERROR: 「{' '.join(command_list)}」 not in format '<string> FROM <string> <params>'.")

        returndict: dict[str, list|str] = {
            "wordEng": command_list[0], "wordFira": command_list[1], "note": "", # Used for the final return
            "subwords": [], # Translations of consituent words
            "append": "", # Additional characters to append to the final word, used for GENDER subcommand
            "with_type": "", "with_params": [] # WITH subcommand and its parameters
            }

        for i in range(len(command_list)-1, -1, -1):
            if command_list[i] in ["WITH", "GENDER", "NOTE"]:
                break
        if i != 0:
            returndict = self.def_word(list(command_list[:i]), iteration=True) # Recursion without this subcommand
            if command_list[i] == "WITH":
                returndict["with_type"] = command_list[i+1]
                returndict["with_params"] = command_list[i+2:]
                command_list = command_list[:i]
            elif command_list[i] == "GENDER":
                gender_dict = {"m": "Masculine", "f": "Feminine", "n": "Neutral", "p": "Plural"}
                returndict["append"] += self.translate([gender_dict[command_list[i+1]], "TO", "Fira"])
            elif command_list[i] == "NOTE":
                returndict["note"] = command_list[i+1]
        else: # Base case
             # Remove engWord and FROM
            returndict["wordEng"] = command_list[0]
            command_list = command_list[2:]
             # Get all subwords
            for _, command in enumerate(command_list):
                if command == "WITH":
                    break
                try:
                    returndict["subwords"].append(self.translate([command, "TO", "Fira"], silent=True))
                except FSError as e:
                    raise FSSyntaxError(f"{func_name} ERROR: Error in 「{' '.join(command_list)}」: {e}") from e

        # Assemble the word
        if not iteration:
            returndict["wordFira"] = ""
            if returndict["with_type"] == "":
                for word in returndict["subwords"]:
                    returndict["wordFira"] += word
            elif returndict["with_type"] == "SLICE":
                for i, word in enumerate(returndict["subwords"]):
                    start = int(returndict["with_params"][i*2])
                    end = int(returndict["with_params"][i*2+1])
                    end = len(word) if end == 0 else end # If end is 0, set it to the end of the word
                    returndict["wordFira"] += word[start:end]
            else:
                raise FSSyntaxError(f"{func_name} ERROR: Invalid WITH type in 「{' '.join(command_list)}」.")
            #print("append", returndict["wordFira"], returndict["append"])
            returndict["wordFira"] += returndict["append"]

        if not silent:
            print("DONE") # Proccessing complete

        return returndict

    def list_word(self, command_list: list[str], **kwargs) -> None:
        '''Lists all words that match a regex string.'''
         # Kwargs
        silent = kwargs.get("silent", True)

        func_name = "LIST"
        if not silent:
            print(func_name, command_list, end=" ... ") # Begin proccessing

        tables: list[sql.Table] = [self.root_word_table, self.word_table]
        if empty(command_list): # If blank, return everything
            conditions = [""]
            columns = ["*"]
        else:
            conditions = [f"wordEng = \"{command_list[0]}\" OR wordFira = \"{command_list[0]}\""]
            columns = ["wordEng", "wordFira"]

        # Check params
        if len(command_list) == 1:
            # No optional params
            pass
        elif len(command_list) > 1:
            while len(command_list) > 1:
                for i in range(len(command_list)-1, -1, -1):
                    if command_list[i] in ["LANG", "TYPE", "NOTE"]:
                        break
                if i == 0:
                    raise FSSyntaxError(f"{func_name} ERROR: Invalid subcommand in 「{' '.join(command_list)}」.")
                if command_list[i] == "LANG":
                    if command_list[i+1] == "e":
                        conditions = [f"wordEng = \"{command_list[0].lower()}\""]
                    elif command_list[i+1] == "f":
                        conditions = [f"wordFira = \"{command_list[0].lower()}\""]
                    else:
                        raise FSSyntaxError(f"{func_name} ERROR: Invalid LANG value in 「{' '.join(command_list)}」.")
                elif command_list[i] == "TYPE":
                    if command_list[i+1] == "r":
                        tables = [self.root_word_table]
                    elif command_list[i+1] == "c":
                        tables = [self.word_table]
                    else:
                        raise FSSyntaxError(f"{func_name} ERROR: Invalid TYPE value in 「{' '.join(command_list)}」.")
                elif command_list[i] == "NOTE":
                    columns.append("note")

                command_list = command_list[:i]

        if not silent:
            print("DONE") # Proccessing complete

        if not empty(conditions):
            for table in tables:
                for row in table.list_record("WHERE "+" AND ".join(conditions), ", ".join(columns)):
                    print(row)
        else:
            for table in tables:
                for row in table.list_record("", ", ".join(columns)):
                    print(row)

    def help(self, **kwargs) -> list[str]:
        '''Prints a list of commands.'''
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
        '''Reads a .fira file and executes the contents.'''
        func_name = "READ"
        if empty(command_list) or len(command_list) != 1:
            raise FSSyntaxError(f"{func_name} ERROR: Invalid number of params in 「{' '.join(command_list)}」.")

        if not re.search(".fira$", command_list[0]):
            raise FSSyntaxError(f"{func_name} ERROR: Invalid file type: 「{command_list[0]}」.")
        try:
            f = file.read(command_list[0], "utf-8")
        except FileNotFoundError as e:
            raise FSSyntaxError(f"{func_name} ERROR: File not found: 「{command_list[0]}」.") from e
        for line_number, file_line in enumerate(f):
            try:
                end = self.decode_input(file_line, depth=depth+1)
                if end:
                    return True
            except FSSyntaxError as e:
                raise FSSyntaxError(f"{func_name} ERROR: Error in file 「{command_list[0]}」 at line {line_number+1}: {e}") from e
        return False

    def decode_input(self, line: str, **kwargs) -> bool:
        '''Reads a line of FiraScript.'''
         # Kwargs
        depth = kwargs.get("depth", 0)

        if depth > self.max_recursion_depth:
            raise FSRecursionError(f"ERROR: Max recursion depth ({self.max_recursion_depth}) reached.")

        command_list = line.split(" ")
        for i, command in enumerate(command_list):
            if command == "": # Skip empty commands
                continue
            if re.search("^\\[", command) is not None: # Check if the command is a group (i.e. it starts with a [)
                if re.search("\\]$", command) is None: # Check if the command is the start of a multi-word String (i.e. it doesn't end with a ])
                    merge_end = -1
                    # Find the end of the string
                    for j in range(i+1, len(command_list)):
                        if re.search("\\]$", command_list[j]):
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
                "\""+defroot_dict["wordEng"].lower()+"\"", 
                "\""+defroot_dict["wordFira"].lower()+"\"", 
                "\""+defroot_dict["note"]+"\"")
        elif command_list[0] == "DEFWORD":
            defword_dict = self.def_word(command_list[1:], silent=self.silent)
            self.word_table.add_record(
                "\""+defword_dict["wordEng"].lower()+"\"", 
                "\""+defword_dict["wordFira"].lower()+"\"", 
                "\""+line+"\"", 
                "\""+defword_dict["note"]+"\"")
        elif command_list[0] == "LIST":
            self.list_word(command_list[1:], silent=self.silent)
        elif command_list[0] == "TRANSLATE":
            print(self.translate(command_list[1:], silent=self.silent).capitalize())
        else:
            raise FSSyntaxError(f"ERROR: Invalid command: 「{command_list[0]}」.")
        return False

    @staticmethod
    def main(db_path: str = "", **kwargs) -> None:
        '''Main function. Do not include the file name in db_path.'''
         # Kwargs
        reset_db = kwargs.get("rdb", False) # True to delete the db file, False to keep it

        db_path = db_path+"fira.db" if (len(db_path) == 0 or db_path[-1] == "/") else db_path+"/fira.db" # Add "fira.db" to db_path
        if reset_db:
            try:
                file.delete(db_path)
            except (PermissionError, FileNotFoundError):
                print(Colours.WARNING, f"Could not delete the db file at db_path.", Colours.ENDC)

        # Set up db connection
        sql_connection = sql.connect(db_path)
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
        print("Enter FiraScript code below. Type 'HELP' for commands.")
        end = False
        while not end:
            user_inp = input("> ")
            try:
                end = fira.decode_input(user_inp)
            except FSError as e:
                print(Colours.FAIL, e, Colours.ENDC)


if __name__ == "__main__":
    FiraScript.main(rdb=True)
