'''
Used to access SQL files. This is a wrapper for Sqlite3.
'''
from sqlite3 import Connection
from sqlite3 import connect as conn
from sqlite3 import Error

class Table:
    '''Initialises a table, which is an object that is used to interface with a specific table within the sql database.'''
    def __init__(self, connection: Connection, table_name: str, fields: list[str]) -> None:
        self._connection = connection
        self._table_name = table_name
        table_formula = f"CREATE TABLE {self._table_name} ("+", ".join(fields)+")"
        try:
            self._connection.cursor().execute(table_formula)
            self._connection.commit()
        except Error:
            pass

    def list_record(self, conditions: str = "", columns: str = "*") -> list[list]:
        '''Lists all recs where the condition is true.'''
        rec_bank = []
        for row in self._connection.cursor().execute(f"""SELECT {columns} FROM {self._table_name} {conditions}"""):
            rec_bank.append(row)
        return rec_bank

    def update_record(self, key: str, value, conditions: str = "") -> bool:
        '''Attempts to update a record. Returns True if an error occurred, and False otherwise.'''
        try:
            self._connection.cursor().execute(f"""UPDATE {self._table_name} SET {key} = {value} {conditions}""")
            self._connection.commit()
        except Error:
            return True
        return False

    def add_record(self, *values) -> bool:
        '''Attempts to add a record. Returns True if an error occurred, and False otherwise.'''
        try:
            self._connection.cursor().execute(f'''INSERT INTO {self._table_name} VALUES ({", ".join(values)})''')
            self._connection.commit()
        except Error:
            return True
        return False


def connect(database_name: str) -> Connection:
    '''Returns the database connection, which needs to be passed into most other functions from this file.'''
    connection = ""
    while connection == "":
        try:
            connection = conn(database_name)
        except Error:
            pass
    return connection

def close_connection(connection: Connection) -> None:
    '''Commits any unsaved changes and closes the connection to the database.'''
    connection.commit()
    connection.close()
