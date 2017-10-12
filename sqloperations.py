# -*- coding: utf-8 -*-

import sqlite3

def execute(dbName, sqlCommands, commit=False):
    """
    Executes commands in a SQLite database, many commands can be executed, they just need
    to be separated by a ; (standard SQL synthax)

    Args:
        dbName: a SQLite database name, ex: 'example.db'
        sqlCommands: string of commands (separated by a ;)
        commit: True commits Changes, False doesn't

    Returns:
        A list of the result(s) of the query(ies)
    """

    conn = sqlite3.Connection(dbName)
    cursor = conn.cursor()
    sqlCommands = sqlCommands.split(';')
    results = []
    for s in sqlCommands:
        try:
            cursor.execute(s)
            query = cursor.fetchall()
            results.append(query)
        except:
            print(s)
        finally:
            if commit is True:
                conn.commit()
    conn.close()
    return results

if __name__ == '__main__':
    # If the module is used directly, do nothing
    pass
