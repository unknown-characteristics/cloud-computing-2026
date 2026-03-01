import json

from http.server import BaseHTTPRequestHandler

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

    def convert_numeric_or_bad_req(self, num):
        try:
            return int(num)
        except:
            self.simple_response_code(404)
            return None