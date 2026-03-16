import json

from . import BaseController
from controllers.participations import ParticipationsController
from controllers.prizes import PrizesController
from models import contest, participation, ranking
from util.database import *

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
            id = self.convert_numeric_or_code(path_parts[0])
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
            elif path_parts[1] == "prizes":
                if command == "GET":
                    PrizesController(self.handler).get_prizes(id, query_dict)
                elif command == "POST":
                    PrizesController(self.handler).post_prize(id)
                else:
                    self.simple_response_code(405)
            elif path_parts[1] == "leaderboard":
                if command == "GET":
                    self.get_leaderboard(id, query_dict)
                else:
                    self.simple_response_code(405)
            else:
                self.simple_response_code(404)
        elif len(path_parts) == 3:
            # path is /contests/{id}/something/{id}
            id = self.convert_numeric_or_code(path_parts[0])
            if id == None:
                return
            
            inner_id = self.convert_numeric_or_code(path_parts[2])
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
                    self.get_individual_ranking(id, inner_id)
                else:
                    self.simple_response_code(405)
            else:
                self.simple_response_code(404)
        else:
            self.simple_response_code(404)

    def get_all_contests(self, query_dict: dict[str, list[str]]):
        out = []
        with DBConnection() as conn, conn.cursor() as cursor:
            sql = f"select {', '.join(contest.Contest.get_lowercase_columns())} from {contest.Contest.get_table_name()} order by id asc"

            result = self.prepare_sql_pagination_filtering_or_bad_req(sql, query_dict, allowed_filter_cols=["difficulty", "status", "name"], date_sort_cols=["start_time_after", "start_time_before", "end_time_after", "end_time_before"], sort_cols=contest.Contest.get_lowercase_columns())
            if result == None:
                return
            
            (sql, params) = result
            for row in cursor.execute(sql, params):
                out += [contest.Contest().from_full_tuple(row)]
        
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
        if "hint" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing hint"))
            return

        if "difficulty" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing difficulty"))
            return
        else:
            req["difficulty"] = self.convert_float_or_code(req["difficulty"], 400)
            if req["difficulty"] == None or not 0 <= req["difficulty"] <= 9:
                self.simple_response_code(400)
                self.output_error(Exception("Invalid difficulty (must be a number between 0 and 9)"))
                return

        if "solution" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing solution"))
            return
        if "id" in req:
            self.simple_response_code(422)
            self.output_error(Exception("ID may not be set"))
            return
        if "start_time" in req:
            self.simple_response_code(422)
            self.output_error(Exception("Start time may not be set"))
            return
        if "end_time" in req:
            self.simple_response_code(422)
            self.output_error(Exception("End time may not be set"))
            return
        
        if "status" not in req:
            req["status"] = "active"
        else:
            if req["status"] not in ["active", "ended"]:
                self.simple_response_code(422)
                self.output_error(Exception("Invalid status (only 'active' or 'ended' are allowed)"))
                return

        if len({col.lower() for col in req.keys()} - set(contest.Contest.get_lowercase_columns())) > 0:
            self.simple_response_code(422)
            self.output_error(Exception("Invalid members in request"))
            return

        with DBConnection() as conn, conn.cursor() as cursor:
            id_var = cursor.var(int)
            params = {"name": req["name"], "hint": req["hint"], "difficulty": req["difficulty"], "solution": req["solution"], "status": req["status"], "id": id_var}

            try:
                cursor.execute("INSERT INTO CONTESTS(name, difficulty, hint, solution, status) VALUES(:name, :difficulty, :hint, :solution, :status) RETURNING id INTO :id", params)
                conn.commit()
            except oracledb.DatabaseError as e:
                error = e.args[0]
                result = contest.Contest.simplify_integrity_error_message(error.code, error.message)
                self.simple_response_code(result[0])
                self.output_error(Exception(result[1]))
                return
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
        if "hint" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing hint"))
            return
        if "difficulty" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing difficulty"))
            return
        else:
            req["difficulty"] = self.convert_numeric_or_code(req["difficulty"], 400)
            if req["difficulty"] == None or not 0 <= req["difficulty"] <= 9:
                self.output_error(Exception("Invalid difficulty"))
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
            self.simple_response_code(422)
            self.output_error(Exception("ID may not be modified"))
            return
        if "start_time" in req:
            self.simple_response_code(422)
            self.output_error(Exception("Start time may not be modified"))
            return
        if "end_time" in req:
            self.simple_response_code(422)
            self.output_error(Exception("End time may not be modified"))
            return
        
        if len({col.lower() for col in req.keys()} - set(contest.Contest.get_lowercase_columns())) > 0:
            self.simple_response_code(422)
            self.output_error(Exception("Invalid members in request"))
            return
        
        with DBConnection() as conn, conn.cursor() as cursor:
            try:
                count = update_by_id(contest.Contest, {"id": id}, req, cursor)
            except oracledb.DatabaseError as e:
                error = e.args[0]
                result = contest.Contest.simplify_integrity_error_message(error.code, error.message)
                self.simple_response_code(result[0])
                self.output_error(Exception(result[1]))
                return

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
            self.simple_response_code(422)
            self.output_error(Exception("ID may not be modified"))
            return

        if "difficulty" in req:
            req["difficulty"] = self.convert_numeric_or_code(req["difficulty"], 400)
            if req["difficulty"] == None or not 0 <= req["difficulty"] <= 9:
                self.output_error(Exception("Invalid difficulty"))
                return

        if "start_time" in req:
            self.simple_response_code(422)
            self.output_error(Exception("Start time may not be modified"))
            return
        if "end_time" in req:
            self.simple_response_code(422)
            self.output_error(Exception("End time may not be modified"))
            return
        
        if len({col.lower() for col in req.keys()} - set(contest.Contest.get_lowercase_columns())) > 0:
            self.simple_response_code(422)
            self.output_error(Exception("Invalid members in request"))
            return
        
        with DBConnection() as conn, conn.cursor() as cursor:
            try:
                count = update_by_id(contest.Contest, {"id": id}, req, cursor)
            except oracledb.DatabaseError as e:
                error = e.args[0]
                result = contest.Contest.simplify_integrity_error_message(error.code, error.message)
                self.simple_response_code(result[0])
                self.output_error(Exception(result[1]))
                return

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
            
            sql = f"select {', '.join(participation.Participation.get_lowercase_columns())} from {participation.Participation.get_table_name()} where contest_id = :contest_id order by contestant_id asc"
            result = self.prepare_sql_pagination_filtering_or_bad_req(sql, query_dict, allowed_filter_cols=["answer"], date_sort_cols=["join_time_after", "join_time_before", "submission_time_after", "submission_time_before"], sort_cols=participation.Participation.get_lowercase_columns())
            if result == None:
                return
            
            (sql, params) = result
            for row in cursor.execute(sql, {"contest_id": id} | params):
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
        if "contest_id" in req:
            req["contest_id"] = self.convert_numeric_or_code(req["contest_id"], 400)
            if req["contest_id"] == None:
                self.output_error(Exception("Invalid contest ID"))
                return

            if req["contest_id"] != id:
                self.simple_response_code(422)
                self.output_error(Exception("Contest ID may not be different between path and request"))
                return
        if "contestant_id" not in req or req["contestant_id"] == None:
            self.simple_response_code(400)
            self.output_error(Exception("Missing contestant ID"))
            return

        if "answer" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing answer"))
            return
        if "score" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing score"))
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
            item = get_by_id(contest.Contest, {"id": id}, cursor)
            if item == None:
                self.simple_response_code(404)
                return

            params = {"contest_id": id, "contestant_id": req["contestant_id"], "answer": req["answer"], "score": req["score"]}

            try:
                cursor.execute("INSERT INTO SUBMISSIONS(contest_id, contestant_id, answer, score) VALUES(:contest_id, :contestant_id, :answer, :score)", params)
                conn.commit()
            except oracledb.DatabaseError as e:
                error = e.args[0]
                result = participation.Participation.simplify_integrity_error_message(error.code, error.message)
                self.simple_response_code(result[0])
                self.output_error(Exception(result[1]))
                return

            item = get_by_id(participation.Participation, {"contest_id": id, "contestant_id": req["contestant_id"]}, cursor)

        self.simple_response_code(201, False)
        self.handler.send_header("Location", f"/contests/{item.contest_id}/participations/{item.contestant_id}")
        self.handler.end_headers()

        self.handler.wfile.write(bytes(json.dumps(item.as_dict()), 'UTF-8'))
        self.handler.wfile.flush()

    def get_leaderboard(self, id: int, query_dict: dict[str, list[str]]):
        out = []
        with DBConnection() as conn, conn.cursor() as cursor:
            item = get_by_id(contest.Contest, {"id": id}, cursor)
            if item == None:
                self.simple_response_code(404)
                return
            
            if item.status != "ended":
                self.simple_response_code(409)
                self.output_error(Exception("Leaderboard is only available after contest end"))
                return

            sql = f"select rownum as rank, contestant_id, submission_time, award_id, score, answer from (select s.contestant_id as contestant_id, s.submission_time as submission_time, a.prize_id as award_id, s.score as score, s.answer as answer from SUBMISSIONS s LEFT JOIN AWARDS a ON s.contest_id = a.contest_id AND s.contestant_id = a.contestant_id where s.contest_id = :contest_id and s.score >= 0.5 order by s.score desc, s.submission_time asc)"
            result = self.prepare_sql_pagination_filtering_or_bad_req(sql, query_dict, allowed_filter_cols=["rank", "contestant_id", "prize_id", "score", "answer"], sort_cols=ranking.Ranking.get_lowercase_columns(), date_sort_cols=["submission_time_after", "submission_time_before"])
            if result == None:
                return
            
            (sql, params) = result
            for row in cursor.execute(sql, params | {"contest_id": id}):
                out += [ranking.Ranking().from_full_tuple(row)]
        
        self.simple_response_code(200)
        self.handler.wfile.write(bytes(json.dumps(out, default=lambda x: x.as_dict()), "UTF-8"))
        self.handler.wfile.flush()

    def get_individual_ranking(self, id: int, contestant_id: int):
        with DBConnection() as conn, conn.cursor() as cursor:
            item = get_by_id(contest.Contest, {"id": id}, cursor)
            if item == None:
                self.simple_response_code(404)
                return
            
            if item.status != "ended":
                self.simple_response_code(409)
                self.output_error(Exception("Leaderboard is only available after contest end"))
                return

            cursor.execute(f"select rownum as rank, contestant_id, submission_time, award_id, score, answer from (select s.contestant_id as contestant_id, s.submission_time as submission_time, a.prize_id as award_id, s.score as score, s.answer as answer from SUBMISSIONS s LEFT JOIN AWARDS a ON s.contest_id = a.contest_id AND s.contestant_id = a.contestant_id where s.contest_id = :contest_id and s.score >= 0.5 order by s.score desc, s.submission_time asc) where contestant_id = :contestant_id", {"contest_id": id, "contestant_id": contestant_id})
            row = cursor.fetchone()
            if row == None:
                self.simple_response_code(404)
                return
    
            item = ranking.Ranking().from_full_tuple(row)
        
        self.simple_response_code(200)
        self.handler.wfile.write(bytes(json.dumps(item, default=lambda x: x.as_dict()), "UTF-8"))
        self.handler.wfile.flush()
