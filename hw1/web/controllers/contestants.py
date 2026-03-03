import json
import oracledb

from . import BaseController
from models import contestant, participation
from util.database import DBConnection, get_by_id, update_by_id, delete_by_id
from controllers.participations import ParticipationsController
from controllers.awards import AwardsController
from util.other import is_valid_email

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
            id = self.convert_numeric_or_code(path_parts[0])
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
            id = self.convert_numeric_or_code(path_parts[0])
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
                    AwardsController(self.handler).get_awards(id, query_dict)
                else:
                    self.simple_response_code(405)
            else:
                self.simple_response_code(404)
        elif len(path_parts) == 3:
            # path is /contestants/{id}/something/{id}
            id = self.convert_numeric_or_code(path_parts[0])
            if id == None:
                return
            
            inner_id = self.convert_numeric_or_code(path_parts[2])
            if inner_id == None:
                return

            if path_parts[1] == "participations":
                if command == "GET":
                    ParticipationsController(self.handler).get_single_participation(inner_id, id)
                elif command == "PUT":
                    ParticipationsController(self.handler).put_participation(inner_id, id)
                elif command == "PATCH":
                    ParticipationsController(self.handler).patch_participation(inner_id, id)
                elif command == "DELETE":
                    ParticipationsController(self.handler).delete_participation(inner_id, id)
                else:
                    self.simple_response_code(405)
            elif path_parts[1] == "awards":
                if command == "GET":
                    AwardsController(self.handler).get_single_award(id, inner_id)
                else:
                    self.simple_response_code(405)
            else:
                self.simple_response_code(404)
        else:
            self.simple_response_code(404)

    def get_all_contestants(self, query_dict: dict[str, list[str]]):
        out = []
        with DBConnection() as conn, conn.cursor() as cursor:
            sql = f"select {', '.join(contestant.Contestant.get_lowercase_columns())} from {contestant.Contestant.get_table_name()}"
            result = self.prepare_sql_pagination_filtering_or_bad_req(sql, query_dict, allowed_filter_cols=["name", "email", "school"], sort_cols=contestant.Contestant.get_lowercase_columns())
            if result == None:
                return
            
            (sql, params) = result
            for row in cursor.execute(sql, params):
                out += [contestant.Contestant().from_full_tuple(row)]
        
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
        else:
            if not is_valid_email(req["email"]):
                self.simple_response_code(422)
                self.output_error(Exception("Invalid email"))
                return

        if "school" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing school"))
            return
        if "id" in req:
            self.simple_response_code(422)
            self.output_error(Exception("ID may not be set"))
            return
        
        if len({col.lower() for col in req.keys()} - set(contestant.Contestant.get_lowercase_columns())) > 0:
            self.simple_response_code(422)
            self.output_error(Exception("Invalid members in request"))
            return
        
        with DBConnection() as conn, conn.cursor() as cursor:
            id_var = cursor.var(int)
            params = {"name": req["name"], "email": req["email"], "school": req["school"], "id": id_var}
            
            try:
                cursor.execute("INSERT INTO CONTESTANTS(name, email, school) VALUES(:name, :email, :school) RETURNING id INTO :id", params)
                conn.commit()
            except oracledb.DatabaseError as e:
                error = e.args[0]
                self.simple_response_code(409)
                self.output_error(Exception(contestant.Contestant.simplify_integrity_error_message(error.code, error.message)))
                return

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
        else:
            if not is_valid_email(req["email"]):
                self.simple_response_code(422)
                self.output_error(Exception("Invalid email"))
                return

        if "school" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing school"))
            return
        if "id" in req and req["id"] != id:
            self.simple_response_code(422)
            self.output_error(Exception("ID may not be modified"))
            return
        
        if len({col.lower() for col in req.keys()} - set(contestant.Contestant.get_lowercase_columns())) > 0:
            self.simple_response_code(422)
            self.output_error(Exception("Invalid members in request"))
            return
        
        with DBConnection() as conn, conn.cursor() as cursor:
            try:
                count = update_by_id(contestant.Contestant, {"id": id}, req, cursor)
            except oracledb.DatabaseError as e:
                error = e.args[0]
                self.simple_response_code(409)
                self.output_error(Exception(contestant.Contestant.simplify_integrity_error_message(error.code, error.message)))
                return

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
            self.simple_response_code(422)
            self.output_error(Exception("ID may not be modified"))
            return
        
        if "email" in req:
            if not is_valid_email(req["email"]):
                self.simple_response_code(422)
                self.output_error(Exception("Invalid email"))
                return

        if len({col.lower() for col in req.keys()} - set(contestant.Contestant.get_lowercase_columns())) > 0:
            self.simple_response_code(422)
            self.output_error(Exception("Invalid members in request"))
            return
        
        with DBConnection() as conn, conn.cursor() as cursor:
            try:
                count = update_by_id(contestant.Contestant, {"id": id}, req, cursor)
            except oracledb.DatabaseError as e:
                error = e.args[0]
                self.simple_response_code(409)
                self.output_error(Exception(contestant.Contestant.simplify_integrity_error_message(error.code, error.message)))
                return

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

            sql = f"select {', '.join(participation.Participation.get_lowercase_columns())} from {participation.Participation.get_table_name()} where contestant_id = :contestant_id"
            result = self.prepare_sql_pagination_filtering_or_bad_req(sql, query_dict, allowed_filter_cols=["answer"], date_sort_cols=["join_time_after", "join_time_before", "submission_time_after", "submission_time_before"], sort_cols=participation.Participation.get_lowercase_columns())
            if result == None:
                return
            
            (sql, params) = result
            for row in cursor.execute(sql, params | {"contestant_id": id}):
                out += [participation.Participation().from_full_tuple(row)]
        
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
        
        if "contest_id" not in req or req["contest_id"] == None:
            self.simple_response_code(400)
            self.output_error(Exception("Missing contest ID"))
            return
        if "answer" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing answer"))
            return
        if "contestant_id" in req:
            req["contestant_id"] = self.convert_numeric_or_code(req["contestant_id"], 400)
            if req["contestant_id"] == None:
                self.output_error(Exception("Invalid contestant ID"))
                return

            if req["contestant_id"] != id:
                self.simple_response_code(422)
                self.output_error(Exception("Contestant ID may not be different between path and request"))
                return
        if "join_time" in req:
            self.simple_response_code(422)
            self.output_error(Exception("Join time may not be set"))
            return
        if "submission_time" in req:
            self.simple_response_code(422)
            self.output_error(Exception("Submission time may not be set"))
            return

        if len({col.lower() for col in req.keys()} - set(participation.Participation.get_lowercase_columns())) > 0:
            self.simple_response_code(422)
            self.output_error(Exception("Invalid members in request"))
            return
        
        with DBConnection() as conn, conn.cursor() as cursor:
            item = get_by_id(contestant.Contestant, {"id": id}, cursor)
            if item == None:
                self.simple_response_code(404)
                return

            params = {"contest_id": req["contest_id"], "contestant_id": id, "answer": req["answer"]}
            try:
                cursor.execute("INSERT INTO SUBMISSIONS(contest_id, contestant_id, answer) VALUES(:contest_id, :contestant_id, :answer)", params)
                conn.commit()
            except oracledb.DatabaseError as e:
                error = e.args[0]
                self.simple_response_code(409)
                self.output_error(Exception(participation.Participation.simplify_integrity_error_message(error.code, error.message)))
                return

            item = get_by_id(participation.Participation, {"contest_id": req["contest_id"], "contestant_id": id}, cursor)

        self.simple_response_code(201, False)
        self.handler.send_header("Location", f"/contestants/{item.contestant_id}/participations/{item.contest_id}")
        self.handler.end_headers()

        self.handler.wfile.write(bytes(json.dumps(item.as_dict()), 'UTF-8'))
        self.handler.wfile.flush()
