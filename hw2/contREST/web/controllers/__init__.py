import json

from http.server import BaseHTTPRequestHandler
from util import database

__all__ = ["contestants", "contests"]

class BaseController:
    handler: BaseHTTPRequestHandler

    def __init__(self, handler: BaseHTTPRequestHandler):
        self.handler = handler

    def simple_response_code(self, code: int, end: bool = True):
        self.handler.send_response(code)
        self.handler.send_header("Content-Type", "application/json")
        if end:
            self.handler.end_headers()

    def output_error(self, exc: Exception):
        self.handler.wfile.write(b'{"msg": "' + bytes(exc.__str__(), 'UTF-8') + b'"}')
        self.handler.wfile.flush()
    
    def get_req_as_json(self):
        size = int(self.handler.headers.get("Content-Length", 0))
        req = None

        if size > 0:
            req = json.loads(self.handler.rfile.read(size))

        return req

    def convert_numeric_or_code(self, num, code=404):
        try:
            return int(num)
        except:
            self.simple_response_code(code)
            return None

    def convert_float_or_code(self, num, code=404):
        try:
            return float(num)
        except:
            self.simple_response_code(code)
            return None

    def prepare_sql_pagination_filtering_or_bad_req(self, sql: str, query_dict: dict[str, list[str]], *, allowed_filter_cols: list[str] | None = None, date_sort_cols: list[str] | None = None, sort_cols: list[str] | None = None) -> tuple[str, dict] | None:
        limit = None
        if "limit" in query_dict:
            limit = self.convert_numeric_or_code(query_dict["limit"][0], 400)
            if limit == None:
                self.output_error(Exception("Invalid limit in query"))
                return None
        offset = None
        if "offset" in query_dict:
            offset = self.convert_numeric_or_code(query_dict["offset"][0], 400)
            if offset == None:
                self.output_error(Exception("Invalid offset in query"))
                return None

        filter_cols = {k: v[0] for k, v in query_dict.items() if k in allowed_filter_cols} if allowed_filter_cols is not None else None
        date_cols = {k: v[0] for k, v in query_dict.items() if k in date_sort_cols} if date_sort_cols is not None else None
        sort_cols = None
        if "sort" in query_dict and sort_cols is not None:
            sort_cols = {k[1:]: (k[0] == '+') for k in query_dict["sort"] if k[1:] in sort_cols}

        return database.add_pagination_and_filtering_to_sql(sql, limit=limit, offset=offset, filter_cols=filter_cols, date_sort_cols=date_cols, sort_cols=sort_cols)
