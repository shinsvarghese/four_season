import sqlite3

class SqlLite(object):
    #class Constructor

    def __init__(self, dbName):
        # Save the Data Base name

        self.dbName = dbName
        if not self.performConnection():
            print('Could Not connect to DB')

    def isSQLite3(self):
        from os.path import isfile, getsize

        if not isfile(self.dbName):
            return False
        if getsize(self.dbName) < 100:  # SQLite database file header is 100 bytes
            return False

        with open(self.dbName, 'rb') as fd:
            header = fd.read(100)
        return header[:16] == b'SQLite format 3\x00'

    def performConnection(self):
        if self.isSQLite3():
            self.conn = sqlite3.connect(self.dbName)
            self.conn.row_factory = self.dict_factory
            return True
        return False

    def ExtractData(self, SqlString):
        return self.conn.execute(SqlString)

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d