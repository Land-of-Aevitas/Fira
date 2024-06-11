'''
The main reader for 'FiraScript'.
'''
 # Library imports
from zemia import sql, file
from zemia.common import Colours
 # Local imports
from fs_errors import FSError
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
                end = fira.instructions.decode(user_inp)
            except FSError as e:
                print(Colours.FAIL, e, Colours.ENDC)


if __name__ == "__main__":
    FiraScript.main(rdb=True)
