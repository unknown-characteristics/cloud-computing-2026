import json

from . import BaseController
from controllers.participations import ParticipationsController
from controllers.prizes import PrizesController
from models import contest, participation, prize
from util.database import DBConnection, get_by_id, update_by_id, delete_by_id

class ContestsController(BaseController):
    def route(self, path_parts: list[str], query_dict: dict[str, list[str]]):
        command = self.handler.command
        if len(path_parts) == 0:
            # path is /contests
            if command == "GET":
                self.get_all_contests(query_dict)
            elif command == "POST":
                self.post_contest()
            else:
                self.simple_response_code(405)
        elif len(path_parts) == 1:
            # path is /contests/{id}
            id = self.convert_numeric_or_bad_req(path_parts[0])
            if id == None:
                return
            
            if command == "GET":
                self.get_single_contest(id)
            elif command == "PUT":
                self.put_contest(id)
            elif command == "PATCH":
                self.patch_contest(id)
            elif command == "DELETE":
                self.delete_contest(id)
            else:
                self.simple_response_code(405)
        elif len(path_parts) == 2:
            # path is /contests/{id}/{something}
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
            elif path_parts[1] == "prizes":
                if command == "GET":
                    PrizesController(self.handler).get_prizes(id, query_dict)
                elif command == "POST":
                    PrizesController(self.handler).post_prize(id)
                else:
                    self.simple_response_code(405)
            elif path_parts[1] == "leaderboard":
                if command == "GET":
                    self.get_leaderboard(id)
                else:
                    self.simple_response_code(405)
            else:
                self.simple_response_code(404)
        elif len(path_parts) == 3:
            # path is /contests/{id}/something/{id}
            id = self.convert_numeric_or_bad_req(path_parts[0])
            if id == None:
                return
            
            inner_id = self.convert_numeric_or_bad_req(path_parts[2])
            if inner_id == None:
                return

            if path_parts[1] == "participations":
                if command == "GET":
                    ParticipationsController(self.handler).get_single_participation(id, inner_id)
                elif command == "PUT":
                    ParticipationsController(self.handler).put_participation(id, inner_id)
                elif command == "PATCH":
                    ParticipationsController(self.handler).patch_participation(id, inner_id)
                elif command == "DELETE":
                    ParticipationsController(self.handler).delete_participation(id, inner_id)
                else:
                    self.simple_response_code(405)
            elif path_parts[1] == "prizes":
                if command == "GET":
                    PrizesController(self.handler).get_single_prize(id, inner_id)
                elif command == "PUT":
                    PrizesController(self.handler).put_prize(id, inner_id)
                elif command == "PATCH":
                    PrizesController(self.handler).patch_prize(id, inner_id)
                elif command == "DELETE":
                    PrizesController(self.handler).delete_prize(id, inner_id)
                else:
                    self.simple_response_code(405)
            elif path_parts[1] == "leaderboard":
                if command == "GET":
                    self.get_individual_leaderboard(id, inner_id)
                else:
                    self.simple_response_code(405)
            else:
                self.simple_response_code(404)
        else:
            self.simple_response_code(404)

    def get_all_contests(self, query_dict: dict[str, list[str]]):
        out = []
        with DBConnection() as conn, conn.cursor() as cursor:
            for row in cursor.execute(f"select rownum as rn, {', '.join(contest.Contest.get_lowercase_columns())} from {contest.Contest.get_table_name()}"):
                out += [contest.Contest().from_full_tuple(row[1:])]
        
        self.simple_response_code(200)
        self.handler.wfile.write(bytes(json.dumps(out, default=lambda x: x.as_dict()), "UTF-8"))
        self.handler.wfile.flush()

    def post_contest(self):
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
        if "difficulty" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing difficulty"))
            return
        if "solution" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing solution"))
            return
        if "id" in req:
            self.simple_response_code(400)
            self.output_error(Exception("ID may not be set"))
            return
        if "start_time" in req:
            self.simple_response_code(400)
            self.output_error(Exception("Start time may not be set"))
            return
        if "end_time" in req:
            self.simple_response_code(400)
            self.output_error(Exception("End time may not be set"))
            return
        
        if "status" not in req:
            req["status"] = "active"
        else:
            if req["status"] not in ["active", "ended"]:
                self.simple_response_code(400)
                self.output_error(Exception("Invalid status (only 'active' or 'ended' are allowed)"))
                return
        
        if len({col.lower() for col in req.keys()} - set(contest.Contest.get_lowercase_columns())) > 0:
            self.simple_response_code(400)
            self.output_error(Exception("Invalid members in request"))
            return
        
        with DBConnection() as conn, conn.cursor() as cursor:
            id_var = cursor.var(int)
            params = {"name": req["name"], "difficulty": req["difficulty"], "solution": req["solution"], "status": req["status"], "id": id_var}
            cursor.execute("INSERT INTO CONTESTS(name, difficulty, solution, status) VALUES(:name, :difficulty, :solution, :status) RETURNING id INTO :id", params)
            conn.commit()

            item = get_by_id(contest.Contest, {"id": id_var.getvalue()[0]}, cursor)

        self.simple_response_code(201, False)
        self.handler.send_header("Location", f"/contests/{item.id}")
        self.handler.end_headers()

        self.handler.wfile.write(bytes(json.dumps(item.as_dict()), 'UTF-8'))
        self.handler.wfile.flush()            

    def delete_contest(self, id):
        with DBConnection() as conn, conn.cursor() as cursor:
            count = delete_by_id(contest.Contest, {"id": id}, cursor)

            if count == 0:
                self.simple_response_code(404)
            else:
                self.simple_response_code(204)
    
    def put_contest(self, id):
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
        if "difficulty" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing difficulty"))
            return
        if "solution" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing solution"))
            return
        if "status" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing status"))
            return
        if "id" in req and req["id"] != id:
            self.simple_response_code(400)
            self.output_error(Exception("ID may not be modified"))
            return
        if "start_time" in req:
            self.simple_response_code(400)
            self.output_error(Exception("Start time may not be modified"))
            return
        if "end_time" in req:
            self.simple_response_code(400)
            self.output_error(Exception("End time may not be modified"))
            return
        
        if len({col.lower() for col in req.keys()} - set(contest.Contest.get_lowercase_columns())) > 0:
            self.simple_response_code(400)
            self.output_error(Exception("Invalid members in request"))
            return
        
        with DBConnection() as conn, conn.cursor() as cursor:
            count = update_by_id(contest.Contest, {"id": id}, req, cursor)

            if count == 0:
                self.simple_response_code(404)
                return

            item = get_by_id(contest.Contest, {"id": id}, cursor)

        self.simple_response_code(200)

        self.handler.wfile.write(bytes(json.dumps(item.as_dict()), 'UTF-8'))
        self.handler.wfile.flush()

    def patch_contest(self, id):
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
        if "start_time" in req:
            self.simple_response_code(400)
            self.output_error(Exception("Start time may not be modified"))
            return
        if "end_time" in req:
            self.simple_response_code(400)
            self.output_error(Exception("End time may not be modified"))
            return
        
        if len({col.lower() for col in req.keys()} - set(contest.Contest.get_lowercase_columns())) > 0:
            self.simple_response_code(400)
            self.output_error(Exception("Invalid members in request"))
            return
        
        with DBConnection() as conn, conn.cursor() as cursor:
            count = update_by_id(contest.Contest, {"id": id}, req, cursor)
            
            if count == 0:
                self.simple_response_code(404)
                return

            item = get_by_id(contest.Contest, {"id": id}, cursor)

        self.simple_response_code(200)

        self.handler.wfile.write(bytes(json.dumps(item.as_dict()), 'UTF-8'))
        self.handler.wfile.flush()

    def get_single_contest(self, id):
        with DBConnection() as conn, conn.cursor() as cursor:
            item = get_by_id(contest.Contest, {"id": id}, cursor)
        
        if item == None:
            self.simple_response_code(404)
        else:
            self.simple_response_code(200)

            self.handler.wfile.write(bytes(json.dumps(item.as_dict()), 'UTF-8'))
            self.handler.wfile.flush()

    def get_contest_participations(self, id: int, query_dict: dict[str, list[str]]):
        out = []
        with DBConnection() as conn, conn.cursor() as cursor:
            item = get_by_id(contest.Contest, {"id": id}, cursor)
            if item == None:
                self.simple_response_code(404)
                return

            for row in cursor.execute(f"select rownum as rn, {', '.join(participation.Participation.get_lowercase_columns())} from {participation.Participation.get_table_name()} where contest_id = :contest_id", {"contest_id": id}):
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
        if "contest_id" in req and req["contest_id"] != id:
            self.simple_response_code(400)
            self.output_error(Exception("Contest ID may not be different between path and request"))
            return
        if "answer" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing answer"))
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
            params = {"contest_id": id, "contestant_id": req["contestant_id"], "answer": req["answer"]}
            cursor.execute("INSERT INTO SUBMISSIONS(contest_id, contestant_id, answer) VALUES(:contest_id, :contestant_id, :answer)", params)
            conn.commit()

            item = get_by_id(participation.Participation, {"contest_id": id, "contestant_id": req["contestant_id"]}, cursor)

        self.simple_response_code(201, False)
        self.handler.send_header("Location", f"/contests/{item.contest_id}/participations/{item.contestant_id}")
        self.handler.end_headers()

        self.handler.wfile.write(bytes(json.dumps(item.as_dict()), 'UTF-8'))
        self.handler.wfile.flush()
