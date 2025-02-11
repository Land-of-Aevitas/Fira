'''
The main reader for 'FiraScript'.
'''
 # Library imports
from zemia import sql
from zemia.common import Colours
 # Local imports
import fs_errors as Fs
from instructions import Instructions

class FiraScript: # pylint: disable=R0903
    '''Methods to decode FiraScript.'''
    def __init__(self, tables: dict[str, sql.Table]) -> None:
        '''Sets the tables for the Instructions.'''
        self.root_word_table = tables["root"]
        self.word_table = tables["complex"]
        self.num_table = tables["num"]
        self.instructions = Instructions()
        self.instructions.set_tables(tables)

    @staticmethod
    def main(db_path: str = "") -> None:
        '''Main function. Do not include the file name in db_path.'''
        # Set up db connection
        sql_connection = sql.connect(db_path)
        tables = {
            "root": sql.Table(
                sql_connection,
                "rootWordTable", 
                [
                    "wordEng STRING NOT NULL", 
                    "wordFira STRING NOT NULL", 
                    "note STRING", 
                    "PRIMARY KEY (wordEng, wordFira)"
                ]
            ),
            "complex": sql.Table(
                sql_connection,
                "wordTable",
                [
                    "wordEng STRING NOT NULL", 
                    "wordFira STRING NOT NULL", 
                    "formula STRING NOT NULL", 
                    "note STRING", 
                    "PRIMARY KEY (wordEng, wordFira)"
                ]
            ),
            "num": sql.Table(
                sql_connection,
                "numTable",
                [
                    "value INT NOT NULL", 
                    "wordEng STRING NOT NULL UNIQUE", 
                    "wordFira STRING NOT NULL UNIQUE", 
                    "note STRING", 
                    "PRIMARY KEY (value)"
                ]
            )
        }
        # Create FiraScript object
        fira = FiraScript(tables)
        # Read input
        print("Enter FiraScript code below. Type 'HELP' for commands.")
        end = False
        while not end:
            user_inp = input("> ")
            try:
                end = fira.instructions.decode(user_inp, db_path=db_path)
            except Fs.FSError as e:
                print(Colours.FAIL, e, Colours.ENDC)


if __name__ == "__main__":
    DATABASE_PATH = "fira.db"
    FiraScript.main(DATABASE_PATH)
