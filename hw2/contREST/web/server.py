import http.server
import os
import urllib.parse
import oracledb

from controllers import *

class RequestHandler(http.server.BaseHTTPRequestHandler):
    def route_request(self):
        urlparse = urllib.parse.urlparse(self.path)
        
        path_parts = urlparse.path.split("/")[1:]
        query_dict = urllib.parse.parse_qs(urlparse.query)

        try:
            if path_parts[0] == "contests":
                contests.ContestsController(self).route(path_parts[1:], query_dict)
            elif path_parts[0] == "contestants":
                contestants.ContestantsController(self).route(path_parts[1:], query_dict)
            else:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
        except oracledb.Error as e:
            print("Oracle error:", e)
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            self.wfile.write(b'{"msg": "Database error"}')
            self.wfile.flush()   
        except Exception as e:
            print("Error:", e)
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            self.wfile.write(b'{"msg": "Unknown error"}')
            self.wfile.flush()

    def do_GET(self):
        self.route_request()
    def do_POST(self):
        self.route_request()
    def do_PUT(self):
        self.route_request()
    def do_DELETE(self):
        self.route_request()
    def do_PATCH(self):
        self.route_request()

server = http.server.HTTPServer(('', int(os.environ.get("SERVER_PORT", 10101))), RequestHandler)

print("Server started!")

server.serve_forever()
