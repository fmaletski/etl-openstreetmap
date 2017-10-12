import sqlite3
import pandas as pd

def execute(dbname):
    """
    Creates a SQLite database from the OSM data

    Args:
        dbName: a SQLite database name, ex: 'example.db'

    Returns:
        Nothing
    """
    conn = sqlite3.Connection(dbname)
    cursor = conn.cursor()
    sqlCommands = '''CREATE TABLE nodes (
        id INTEGER PRIMARY KEY NOT NULL,
        lat REAL,
        lon REAL,
        user TEXT,
        uid INTEGER,
        version INTEGER,
        changeset INTEGER,
        timestamp TEXT
    );

    CREATE TABLE nodes_tags (
        id INTEGER,
        key TEXT,
        value TEXT,
        type TEXT,
        FOREIGN KEY (id) REFERENCES nodes(id)
    );

    CREATE TABLE ways (
        id INTEGER PRIMARY KEY NOT NULL,
        user TEXT,
        uid INTEGER,
        version TEXT,
        changeset INTEGER,
        timestamp TEXT
    );

    CREATE TABLE ways_tags (
        id INTEGER NOT NULL,
        key TEXT NOT NULL,
        value TEXT NOT NULL,
        type TEXT,
        FOREIGN KEY (id) REFERENCES ways(id)
    );

    CREATE TABLE ways_nodes (
        id INTEGER NOT NULL,
        node_id INTEGER NOT NULL,
        position INTEGER NOT NULL,
        FOREIGN KEY (id) REFERENCES ways(id),
        FOREIGN KEY (node_id) REFERENCES nodes(id)
    )
    '''
    sqlCommands = sqlCommands.split(';')
    for s in sqlCommands:
        try:
            cursor.execute(s)
        except:
            print(s)
        finally:
            conn.commit()

    CSV_FILES = ['nodes.csv', 'nodes_tags.csv', 'ways.csv', 'ways_nodes.csv', 'ways_tags.csv']
    TABLE_NAMES = ['nodes', 'nodes_tags', 'ways', 'ways_nodes', 'ways_tags']
    NAMES = zip(CSV_FILES, TABLE_NAMES)

    for fname, table in NAMES:
        df = pd.read_csv(fname, encoding='utf-8')
        df.to_sql(table, conn, if_exists='replace', index=False)
        # Uses pandas to handle secure database insertion.
        # Can be a problem if the data is bigger than the available memory,
        # But for this project it works perfectly.

    conn.close()

if __name__ == '__main__':
    # If the module is used directly, execute the main function with standard arguments
    execute('curitiba.db')
