import json

from . import BaseController
from models import contestant, participation
from util.database import DBConnection, get_by_id, update_by_id, delete_by_id
from controllers.participations import ParticipationsController

class ContestantsController(BaseController):
    def route(self, path_parts: list[str], query_dict: dict[str, list[str]]):
        command = self.handler.command
        if len(path_parts) == 0:
            # path is /contestants
            if command == "GET":
                self.get_all_contestants(query_dict)
            elif command == "POST":
                self.post_contestant()
            else:
                self.simple_response_code(405)
        elif len(path_parts) == 1:
            # path is /contestants/{id}
            id = self.convert_numeric_or_bad_req(path_parts[0])
            if id == None:
                return
            
            if command == "GET":
                self.get_single_contestant(id)
            elif command == "PUT":
                self.put_contestant(id)
            elif command == "PATCH":
                self.patch_contestant(id)
            elif command == "DELETE":
                self.delete_contestant(id)
            else:
                self.simple_response_code(405)
        elif len(path_parts) == 2:
            # path is /contestants/{id}/{something}
            id = self.convert_numeric_or_bad_req(path_parts[0])
            if id == None:
                return

            if path_parts[1] == "participations":
                if command == "GET":
                    self.get_contest_participations(id, query_dict)
                elif command == "POST":
                    self.post_contest_participation(id)
                else:
                    self.simple_response_code(405)
            elif path_parts[1] == "awards":
                if command == "GET":
                    self.get_awards(id)
                else:
                    self.simple_response_code(405)
            else:
                self.simple_response_code(404)
        elif len(path_parts) == 3:
            # path is /contestants/{id}/something/{id}
            id = self.convert_numeric_or_bad_req(path_parts[0])
            if id == None:
                return
            
            inner_id = self.convert_numeric_or_bad_req(path_parts[2])
            if inner_id == None:
                return

            if path_parts[1] == "participations":
                if command == "GET":
                    ParticipationsController().get_single_participation(id, inner_id)
                elif command == "PUT":
                    ParticipationsController().put_participation(id, inner_id)
                elif command == "PATCH":
                    ParticipationsController().patch_participation(id, inner_id)
                elif command == "DELETE":
                    ParticipationsController().delete_participation(id, inner_id)
                else:
                    self.simple_response_code(405)
            elif path_parts[1] == "awards":
                if command == "GET":
                    self.get_single_award(id, inner_id)
                else:
                    self.simple_response_code(405)
            else:
                self.simple_response_code(404)
        else:
            self.simple_response_code(404)

    def get_all_contestants(self, query_dict: dict[str, list[str]]):
        out = []
        with DBConnection() as conn, conn.cursor() as cursor:
            for row in cursor.execute(f"select rownum as rn, {', '.join(contestant.Contestant.get_lowercase_columns())} from {contestant.Contestant.get_table_name()}"):
                out += [contestant.Contestant().from_full_tuple(row[1:])]
        
        self.simple_response_code(200)
        self.handler.wfile.write(bytes(json.dumps(out, default=lambda x: x.as_dict()), "UTF-8"))
        self.handler.wfile.flush()

    def post_contestant(self):
        try:
            req = self.get_req_as_json()
        except:
            self.simple_response_code(400)
            self.output_error(Exception("Invalid request body JSON"))
            return

        if req == None:
            self.simple_response_code(400)
            self.output_error(Exception("Missing body"))
            return
        
        if "name" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing name"))
            return
        if "email" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing email"))
            return
        if "school" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing school"))
            return
        if "id" in req:
            self.simple_response_code(400)
            self.output_error(Exception("ID may not be set"))
            return
        
        if len({col.lower() for col in req.keys()} - set(contestant.Contestant.get_lowercase_columns())) > 0:
            self.simple_response_code(400)
            self.output_error(Exception("Invalid members in request"))
            return
        
        with DBConnection() as conn, conn.cursor() as cursor:
            id_var = cursor.var(int)
            params = {"name": req["name"], "email": req["email"], "school": req["school"], "id": id_var}
            cursor.execute("INSERT INTO CONTESTANTS(name, email, school) VALUES(:name, :email, :school) RETURNING id INTO :id", params)
            conn.commit()

            item = get_by_id(contestant.Contestant, {"id": id_var.getvalue()[0]}, cursor)

        self.simple_response_code(201, False)
        self.handler.send_header("Location", f"/contestants/{item.id}")
        self.handler.end_headers()

        self.handler.wfile.write(bytes(json.dumps(item.as_dict()), 'UTF-8'))
        self.handler.wfile.flush()            

    def delete_contestant(self, id):
        with DBConnection() as conn, conn.cursor() as cursor:
            count = delete_by_id(contestant.Contestant, {"id": id}, cursor)

            if count == 0:
                self.simple_response_code(404)
            else:
                self.simple_response_code(204)
    
    def put_contestant(self, id):
        try:
            req = self.get_req_as_json()
        except:
            self.simple_response_code(400)
            self.output_error(Exception("Invalid request body JSON"))
            return

        if req == None:
            self.simple_response_code(400)
            self.output_error(Exception("Missing body"))
            return
        
        if "name" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing name"))
            return
        if "email" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing email"))
            return
        if "school" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing school"))
            return
        if "id" in req and req["id"] != id:
            self.simple_response_code(400)
            self.output_error(Exception("ID may not be modified"))
            return
        
        if len({col.lower() for col in req.keys()} - set(contestant.Contestant.get_lowercase_columns())) > 0:
            self.simple_response_code(400)
            self.output_error(Exception("Invalid members in request"))
            return
        
        with DBConnection() as conn, conn.cursor() as cursor:
            count = update_by_id(contestant.Contestant, {"id": id}, req, cursor)

            if count == 0:
                self.simple_response_code(404)
                return

            item = get_by_id(contestant.Contestant, {"id": id}, cursor)

        self.simple_response_code(200)

        self.handler.wfile.write(bytes(json.dumps(item.as_dict()), 'UTF-8'))
        self.handler.wfile.flush()

    def patch_contestant(self, id):
        try:
            req = self.get_req_as_json()
        except:
            self.simple_response_code(400)
            self.output_error(Exception("Invalid request body JSON"))
            return

        if req == None:
            self.simple_response_code(400)
            self.output_error(Exception("Missing body"))
            return
        
        if "id" in req and req["id"] != id:
            self.simple_response_code(400)
            self.output_error(Exception("ID may not be modified"))
            return
        
        if len({col.lower() for col in req.keys()} - set(contestant.Contestant.get_lowercase_columns())) > 0:
            self.simple_response_code(400)
            self.output_error(Exception("Invalid members in request"))
            return
        
        with DBConnection() as conn, conn.cursor() as cursor:
            count = update_by_id(contestant.Contestant, {"id": id}, req, cursor)
            
            if count == 0:
                self.simple_response_code(404)
                return

            item = get_by_id(contestant.Contestant, {"id": id}, cursor)

        self.simple_response_code(200)

        self.handler.wfile.write(bytes(json.dumps(item.as_dict()), 'UTF-8'))
        self.handler.wfile.flush()

    def get_single_contestant(self, id):
        with DBConnection() as conn, conn.cursor() as cursor:
            item = get_by_id(contestant.Contestant, {"id": id}, cursor)
        
        if item == None:
            self.simple_response_code(404)
        else:
            self.simple_response_code(200)

            self.handler.wfile.write(bytes(json.dumps(item.as_dict()), 'UTF-8'))
            self.handler.wfile.flush()

    def get_contest_participations(self, id: int, query_dict: dict[str, list[str]]):
        out = []
        with DBConnection() as conn, conn.cursor() as cursor:
            item = get_by_id(contestant.Contestant, {"id": id}, cursor)
            if item == None:
                self.simple_response_code(404)
                return

            for row in cursor.execute(f"select rownum as rn, {', '.join(participation.Participation.get_lowercase_columns())} from {participation.Participation.get_table_name()} where contestant_id = :contestant_id", {"contestant_id": id}):
                out += [participation.Participation().from_full_tuple(row[1:])]
        
        self.simple_response_code(200)
        self.handler.wfile.write(bytes(json.dumps(out, default=lambda x: x.as_dict()), "UTF-8"))
        self.handler.wfile.flush()
    
    def post_contest_participation(self, id: int):
        try:
            req = self.get_req_as_json()
        except:
            self.simple_response_code(400)
            self.output_error(Exception("Invalid request body JSON"))
            return

        if req == None:
            self.simple_response_code(400)
            self.output_error(Exception("Missing body"))
            return
        
        if "contestant_id" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing contestant ID"))
            return
        if "answer" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing answer"))
            return
        if "contest_id" in req and req["contest_id"] != id:
            self.simple_response_code(400)
            self.output_error(Exception("Contest ID may not be different between path and request"))
            return
        if "join_time" in req:
            self.simple_response_code(400)
            self.output_error(Exception("Join time may not be set"))
            return
        if "submission_time" in req:
            self.simple_response_code(400)
            self.output_error(Exception("Submission time may not be set"))
            return

        if len({col.lower() for col in req.keys()} - set(participation.Participation.get_lowercase_columns())) > 0:
            self.simple_response_code(400)
            self.output_error(Exception("Invalid members in request"))
            return
        
        with DBConnection() as conn, conn.cursor() as cursor:
            params = {"contest_id": req["contest_id"], "contestant_id": id, "answer": req["answer"]}
            cursor.execute("INSERT INTO SUBMISSIONS(contest_id, contestant_id, answer) VALUES(:contest_id, :contestant_id, :answer)", params)
            conn.commit()

            item = get_by_id(participation.Participation, {"contest_id": req["contest_id"], "contestant_id": id}, cursor)

        self.simple_response_code(201, False)
        self.handler.send_header("Location", f"/contestants/{item.contestant_id}/participations/{item.contest_id}")
        self.handler.end_headers()

        self.handler.wfile.write(bytes(json.dumps(item.as_dict()), 'UTF-8'))
        self.handler.wfile.flush()
