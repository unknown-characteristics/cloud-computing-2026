import oracledb
import os
import json

class ConnectionParameters:
    user: str
    password: str
    dsn: str

    def __init__(self, user, password, dsn):
        self.user = user
        self.password = password
        self.dsn = dsn

def get_default_parameters() -> ConnectionParameters:
    default_path = os.path.join(os.path.dirname(__file__), "default_credentials.json")
    with open(default_path) as file:
        creds = json.load(file)
    
    dsn = os.environ.get("DB_HOST", "localhost") + "/PDBCONTREST"

    return ConnectionParameters(creds["user"], creds["password"], dsn)

class DBConnection:
    parameters: ConnectionParameters
    conn: oracledb.Connection

    def __init__(self, parameters = get_default_parameters()):
        self.parameters = parameters

    def __enter__(self) -> oracledb.Connection:
        self.conn = oracledb.connect(user=self.parameters.user, password=self.parameters.password, dsn=self.parameters.dsn)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

        return False
    
def get_by_id(cls, ids: dict[str, int], cursor: oracledb.Cursor):
    query_cond = ' AND '.join([f'{n} = :{n}' for n in ids.keys()])

    cursor.execute(f"SELECT * FROM {cls.get_table_name()} WHERE {query_cond}", ids)
    tuple = cursor.fetchone()
    if tuple == None:
        return None
    
    item = cls().from_full_tuple(tuple)

    return item

def update_by_id(cls, ids: dict[str, int], cols: dict[str, int], cursor: oracledb.Cursor):
    query_cond = ' AND '.join([f'{n} = :{n}' for n in ids.keys()])
    update_str = ', '.join([f'{c} = :{c}' for c in cols.keys() if c not in ids])

    params = ids | cols # union
    cursor.execute(f"UPDATE {cls.get_table_name()} SET {update_str} WHERE {query_cond}", params)
    cursor.connection.commit()

    return cursor.rowcount

def delete_by_id(cls, ids: dict[str, int], cursor: oracledb.Cursor):
    query_cond = ' AND '.join([f'{n} = :{n}' for n in ids.keys()])

    cursor.execute(f"DELETE FROM {cls.get_table_name()} WHERE {query_cond}", ids)
    cursor.connection.commit()

    return cursor.rowcount
