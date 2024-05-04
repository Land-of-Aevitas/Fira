'''
The main reader for 'FiraScript'.
'''
import sql_lib as sql

FILE_LOC = "./Fira"

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
    with open(f"{FILE_LOC}/{filename}", "r", encoding="utf-8") as f:
        content = f.read().splitlines()

    for line in content:
        print(line)

read_file("test.fira")


sql_connection = sql.connect(f"{FILE_LOC}/fira.db")
root_word_table = RootWordTable(sql_connection)
