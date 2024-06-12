'''Instructions module for the FiraScript language.'''
import re
from zemia.common import empty
from zemia import sql, file
 # Local imports
from fs_errors import FSError, FSSyntaxError, FSRecursionError

class Instructions:
    '''Instructions for the FiraScript language.'''
    def __init__(self) -> None:
         # Settings - can be changed with the DEBUG command
        self.silent = True
        self.max_recursion_depth = 10
        self.print_read = False

    END_DICT = {"m": "_Masculine", "f": "_Feminine", "n": "_Neutral", "p": "_Plural", "v": "_Verb"} # Used for the END subcommand
    DIGIT_WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"] # Used for DEFNUM
    root_word_table: sql.Table = None
    word_table: sql.Table = None
    num_table: sql.Table = None

    def set_tables(self, tables: dict[str, sql.Table]) -> None:
        '''Sets the tables for the Instructions.'''
        self.root_word_table = tables["root"]
        self.word_table = tables["complex"]
        self.num_table = tables["num"]


    def decode(self, line: str, **kwargs) -> bool:
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
        match command_list[0]:
            case "" | "#":
                pass
            case "DEFROOT":
                defroot_dict = self.defroot(command_list[1:], silent=self.silent)
                self.root_word_table.add_record(
                    f"\"{defroot_dict["wordEng"].lower()}\"",
                    f"\"{defroot_dict["wordFira"].lower()}\"",
                    f"\"{defroot_dict["note"]}\""
                )
            case "DEFWORD":
                defword_dict = self.defword(command_list[1:], silent=self.silent)
                self.word_table.add_record(
                    f"\"{defword_dict["wordEng"].lower()}\"",
                    f"\"{defword_dict["wordFira"].lower()}\"",
                    f"\"{line}\"",
                    f"\"{defword_dict["note"]}\""
                )
            case "DEFNUM":
                defnum_dict = self.defnum(command_list[1:], silent=self.silent)
                self.num_table.add_record(
                    f"\"{defnum_dict["value"]}\"",
                    f"\"{defnum_dict["wordEng"].lower()}\"",
                    f"\"{defnum_dict["wordFira"].lower()}\"",
                    f"\"{defnum_dict["note"]}\""
                )
            case "LISTWORDS":
                self.listwords(command_list[1:], silent=self.silent)
            case "TRANSLATE":
                print(self.translate(command_list[1:], silent=self.silent).capitalize())
            case "UPDATE":
                self.update(command_list[1:], silent=self.silent)
            case "DELETE":
                self.delete(command_list[1:], silent=self.silent)
            case "HELP":
                for i in self.help(silent=self.silent):
                    print(i)
            case "READ":
                return self.read(command_list[1:], depth)
            case "DEBUG":
                self.debug(command_list[1:])
            case "#": # Comment
                pass
            case "EXIT":
                return True
            case _: # Implicit TRANSLATE
                #raise FSSyntaxError(f"ERROR: Invalid command: 「{command_list[0]}」.")
                print(self.translate(command_list+["TO","f"], silent=self.silent).capitalize())
        return False

    def defroot(self, command_list: list[str], **kwargs) -> dict[str, str]:
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
                match command_list[i]:
                    case "END":
                        returndict = self.defroot(command_list[:i]) # Recursion without this subcommand
                        returndict["wordFira"] += self.translate(self.END_DICT[command_list[i+1]]+["TO","f"])
                        break
                    case "NOTE":
                        returndict = self.defroot(command_list[:i]) # Recursion without this subcommand
                        returndict["note"] = command_list[i+1]
                        break
            if i == 0:
                raise FSSyntaxError(f"{func_name} ERROR: Invalid subcommand in 「{' '.join(command_list)}」.")

        if not silent:
            print("DONE") # Proccessing complete

        return returndict

    def defword(self, command_list: list[str], **kwargs) -> dict[str, list|str]:
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
            "append": "", # Additional characters to append to the final word, used for END subcommand
            "with_type": "", "with_params": [] # WITH subcommand and its parameters
            }

        for i in range(len(command_list)-1, -1, -1):
            match command_list[i]:
                case "WITH":
                    returndict = self.defword(list(command_list[:i]), iteration=True) # Recursion without this subcommand
                    returndict["with_type"] = command_list[i+1]
                    returndict["with_params"] = command_list[i+2:]
                    command_list = command_list[:i]
                    break
                case "END":
                    returndict = self.defword(list(command_list[:i]), iteration=True) # Recursion without this subcommand
                    returndict["append"] += self.translate([self.END_DICT[command_list[i+1]], "TO", "Fira"])
                    break
                case "NOTE":
                    returndict = self.defword(list(command_list[:i]), iteration=True) # Recursion without this subcommand
                    returndict["note"] = command_list[i+1]
                    break
        if i == 0: # Base case
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
            match returndict["with_type"]:
                case "":
                    for word in returndict["subwords"]:
                        returndict["wordFira"] += word
                case "SLICE":
                    for i, word in enumerate(returndict["subwords"]):
                        start = int(returndict["with_params"][i*2])
                        end = int(returndict["with_params"][i*2+1])
                        end = len(word) if end == 0 else end # If end is 0, set it to the end of the word
                        returndict["wordFira"] += word[start:end]
                case "JOIN":
                    match len(returndict["with_params"]):
                        case 0:
                            returndict["wordFira"] = "".join(returndict["subwords"])
                        case 1:
                            returndict["wordFira"] = returndict["with_params"][0].join(returndict["subwords"])
                        case _:
                            raise FSSyntaxError(f"{func_name} ERROR: Invalid number of with_params in 「{' '.join(command_list)}」.")
                case "DERIVE":
                    if len(returndict["subwords"]) != 1:
                        raise FSSyntaxError(f"{func_name} ERROR: WITH DERIVE must only have one subword 「{' '.join(command_list)}」.")
                    if len(returndict["with_params"]) != 1:
                        raise FSSyntaxError(f"{func_name} ERROR: Invalid number of with_params in 「{' '.join(command_list)}」.")
                    der_word, der_type = "", ""
                    match returndict["with_params"][0].lower():
                        case "i"|"instance":
                            der_word, der_type = "_Instance", "Instance"
                        case "s"|"subject":
                            der_word, der_type = "_Subject", "Subject"
                        case "o"|"object":
                            der_word, der_type = "_Object", "Object"
                        case "p"|"place":
                            der_word, der_type = "_Place", "Place"
                        case "v"|"verb":
                            der_word, der_type = "_Verb", "Verb"
                        case _:
                            raise FSSyntaxError(f"{func_name} ERROR: Invalid with_params value in 「{' '.join(command_list)}」.")
                    derive = ""
                    try:
                        derive = self.translate([der_word, "TO", "f"])
                    except FSError as e:
                        raise FSSyntaxError(f"{func_name} ERROR: WITH DERIVE {der_type} Error: {e} in 「{' '.join(command_list)}」") from e
                    returndict["wordFira"] = returndict["subwords"][0]+derive
                case _:
                    raise FSSyntaxError(f"{func_name} ERROR: Invalid WITH type in 「{' '.join(command_list)}」.")
            returndict["wordFira"] += returndict["append"]

        if not silent:
            print("DONE") # Proccessing complete

        return returndict

    def _translate_num(self, num: int|str, **kwargs) -> str|list[str]:
        '''ONLY USED BY DEFNUM for recursion. Translates a number.'''
         # Kwargs
        silent = kwargs.get("silent", True)
        fold = kwargs.get("fold", True)

        func_name = "TRANSLATE_NUM"
        if not silent:
            print(func_name, num, end=" ... ") # Begin proccessing

        in_zero, zero_count = False, 0
        translated_num = []
        for _, digit in enumerate(str(num)):
            if digit == "0":
                if in_zero:
                    zero_count += 1
                else:
                    in_zero = True
                    zero_count = 1
            else:
                if in_zero:
                    translated_num.append(self.translate(["Zero", "TO", "f"]))
                    if zero_count > 1:
                        translated_num.append(*self._translate_num(zero_count, fold=False))
                    translated_num.append(self.translate(["And", "TO", "f"]))
                    in_zero = False
                translated_num.append(self.translate([self.DIGIT_WORDS[int(digit)], "TO", "f"]))
        if in_zero: # Trailing zeros
            translated_num.append(self.translate(["Zero", "TO", "f"]))
            if zero_count > 1:
                translated_num.append(*self._translate_num(zero_count, fold=False))

        if not silent:
            print("translated_num", translated_num)
            print("DONE") # Proccessing complete

        return "-".join(translated_num) if fold else translated_num

    def defnum(self, command_list: list[str], **kwargs) -> dict[str, int|str]:
        '''Defines a number.'''
         # Kwargs
        silent = kwargs.get("silent", True)

        func_name = "DEFNUM"
        if not silent:
            print(func_name, command_list, end=" ... ") # Begin proccessing

        if empty(command_list):
            raise FSSyntaxError(f"{func_name} ERROR: No params provided in 「{' '.join(command_list)}」.")
        if len(command_list) < 2:
            raise FSSyntaxError(f"{func_name} ERROR: Invalid number of params in 「{' '.join(command_list)}」.")
        try:
            value = int(command_list[1])
        except ValueError as e:
            raise FSSyntaxError(f"{func_name} ERROR: Invalid value in 「{' '.join(command_list)}」.") from e

        returndict: dict[str, int|str] = {
            "wordEng": command_list[0],
            "wordFira": self._translate_num(value),
            "value": value,
            "note": ""
        }

        while len(command_list) > 2: # Has optional params
            for i in range(len(command_list)-1, -1, -1):
                match command_list[i]:
                    case "NOTE":
                        returndict["note"] = command_list[i+1]
            if i == 0:
                raise FSSyntaxError(f"{func_name} ERROR: Invalid subcommand in 「{' '.join(command_list)}」.")
            command_list = command_list[:i] # Remove the subcommand

        if not silent:
            print("DONE") # Proccessing complete

        return returndict


    def listwords(self, command_list: list[str], **kwargs) -> None:
        '''Lists all words that match a regex string.'''
         # Kwargs
        silent = kwargs.get("silent", True)

        func_name = "LISTWORDS"
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
        while len(command_list) > 1: # Has optional params
            for i in range(len(command_list)-1, -1, -1):
                match command_list[i]:
                    case "LANG":
                        match command_list[i+1]:
                            case "e":
                                conditions = [f"wordEng = \"{command_list[0]}\""]
                            case "f":
                                conditions = [f"wordFira = \"{command_list[0]}\""]
                            case _:
                                raise FSSyntaxError(f"{func_name} ERROR: Invalid LANG value in 「{' '.join(command_list)}」.")
                    case "TYPE":
                        match command_list[i+1]:
                            case "r":
                                tables = [self.root_word_table]
                            case "c":
                                tables = [self.word_table]
                            case _:
                                raise FSSyntaxError(f"{func_name} ERROR: Invalid TYPE value in 「{' '.join(command_list)}」.")
                    case "NOTE":
                        columns.append("note")
            if i == 0:
                raise FSSyntaxError(f"{func_name} ERROR: Invalid subcommand in 「{' '.join(command_list)}」.")
            command_list = command_list[:i] # Remove the last subcommand

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

    def update(self, command_list: list[str], **kwargs) -> None:
        '''Updates a word.'''
         # Kwargs
        silent = kwargs.get("silent", True)

        func_name = "UPDATE"
        if not silent:
            print(func_name, command_list, end=" ... ") # Begin proccessing

        if empty(command_list):
            raise FSSyntaxError(f"{func_name} ERROR: No params provided in 「{' '.join(command_list)}」.")
        if len(command_list) != 2:
            raise FSSyntaxError(f"{func_name} ERROR: Invalid number of params in 「{' '.join(command_list)}」.")

        word_eng, word_fira = command_list[0].lower(), command_list[1].lower()
        if not self.root_word_table.update_record("wordFira", f"\"{word_fira}\"", f"WHERE wordEng = \"{word_eng}\""):
            raise FSSyntaxError(f"{func_name} ERROR: No record found for 「{' '.join(command_list)}」.")

        if not silent:
            print("DONE") # Proccessing complete

    def delete(self, command_list: list[str], **kwargs) -> None:
        '''Deletes a word.'''
         # Kwargs
        silent = kwargs.get("silent", True)

        func_name = "DELETE"
        if not silent:
            print(func_name, command_list, end=" ... ") # Begin proccessing

        if empty(command_list):
            raise FSSyntaxError(f"{func_name} ERROR: No params provided in 「{' '.join(command_list)}」.")
        if len(command_list) != 1:
            raise FSSyntaxError(f"{func_name} ERROR: 「{' '.join(command_list)}」 not in format '<string>'.")
        self.root_word_table.delete_record(f"WHERE wordEng = \"{command_list[0].lower()}\" OR wordFira = \"{command_list[0].lower()}\"")
        self.word_table.delete_record(f"WHERE wordEng = \"{command_list[0].lower()}\" OR wordFira = \"{command_list[0].lower()}\"")

        if not silent:
            print("DONE") # Proccessing complete

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

         # Check for errors
        if empty(command_list) or len(command_list) != 1:
            raise FSSyntaxError(f"{func_name} ERROR: Invalid number of params in 「{' '.join(command_list)}」.")
        if not re.search(".fira$", command_list[0]):
            raise FSSyntaxError(f"{func_name} ERROR: Invalid file type: 「{command_list[0]}」.")
        try:
            f = file.read(command_list[0], "utf-8")
        except FileNotFoundError as e:
            raise FSSyntaxError(f"{func_name} ERROR: File not found: 「{command_list[0]}」.") from e

         # Read the file line by line
        for line_number, file_line in enumerate(f):
            if self.print_read:
                print(f"Reading {command_list[0]} line {line_number+1}: {file_line}")
            try:
                end = self.decode(file_line, depth=depth+1)
                if end:
                    return True
            except FSSyntaxError as e:
                raise FSSyntaxError(f"{func_name} ERROR: Error in file 「{command_list[0]}」 at line {line_number+1}: {e}") from e
        return False

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
        match command_list[i]:
            case "SILENT":
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
            case "MAX-RECUR":
                old_max = self.max_recursion_depth
                if i == len(command_list)-1: # No param
                    self.max_recursion_depth = 10
                else:
                    try:
                        self.max_recursion_depth = int(command_list[i+1])
                    except ValueError as e:
                        raise FSSyntaxError(f"{func_name} ERROR: Invalid MAX-RECUR value in 「{' '.join(command_list)}」.") from e
                print(f"Max recursion depth updated from {old_max} to {self.max_recursion_depth}.")
            case "PRINT-READ": # Toggle printing the current read file line number
                if i == len(command_list)-1: # No param
                    self.print_read = not self.print_read
                else:
                    if command_list[i+1].lower() in ["true", "t", "1"]:
                        self.print_read = True
                    elif command_list[i+1].lower() in ["false", "f", "0"]:
                        self.print_read = False
                    else:
                        raise FSSyntaxError(f"{func_name} ERROR: Invalid PRINT-READ value in 「{' '.join(command_list)}」.")
            case _:
                raise FSSyntaxError(f"{func_name} ERROR: Invalid subcommand in 「{' '.join(command_list)}」.")
