import oracledb
import os
import json

from dateutil import parser
from datetime import timezone

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

def add_pagination_and_filtering_to_sql(sql: str, *, limit: int | None = None, offset: int | None = None, filter_cols: dict[str, str] | None = None, date_sort_cols: dict[str, tuple[bool, str]] | None = None, sort_cols: dict[str, bool] | None = None) -> tuple[str, dict]:
    params = {}

    sql = 'select * from (' + sql + ')'
    where_text = ''
    if filter_cols != None and len(filter_cols) > 0:
        where_text = ' and '.join([f'{c} = :{c}' for c in filter_cols])
        params = params | filter_cols

    if date_sort_cols != None and len(date_sort_cols) > 0:
        for col in date_sort_cols:
            if col.endswith("_after"):
                real_col_text = col[:-6]
                where_text = where_text + f' and {real_col_text} >= :{real_col_text}'
                params[real_col_text] = parser.isoparse(date_sort_cols[col]).astimezone(timezone.utc)
            elif col.endswith("_before"):
                real_col_text = col[:-7]
                where_text = where_text + f' and {real_col_text} <= :{real_col_text}'
                params[real_col_text] = parser.isoparse(date_sort_cols[col]).astimezone(timezone.utc)

    if where_text != '':
        sql = sql + ' where ' + where_text

    if sort_cols != None and len(sort_cols) > 0 :
        order_text = ', '.join([f'{c} {"asc" if asc else "desc"}' for c, asc in sort_cols.items()])
        sql = sql + ' order by ' + order_text

    if offset != None:
        sql = sql + " OFFSET :offset ROWS"
        params["offset"] = offset

    if limit != None:
        sql = sql + " FETCH NEXT :limit ROWS ONLY"
        params["limit"] = limit

    return (sql, params)
