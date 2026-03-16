import json
import oracledb

from . import BaseController
from models import prize, contest
from util.database import DBConnection, get_by_id, update_by_id, delete_by_id

class PrizesController(BaseController):
    def get_prizes(self, contest_id: int, query_dict: dict[str, list[str]]):
        out = []
        with DBConnection() as conn, conn.cursor() as cursor:
            item = get_by_id(contest.Contest, {"id": contest_id}, cursor)
            if item == None:
                self.simple_response_code(404)
                return
            
            sql = f"select {', '.join(prize.Prize.get_lowercase_columns())} from {prize.Prize.get_table_name()} where contest_id = :contest_id"
            result = self.prepare_sql_pagination_filtering_or_bad_req(sql, query_dict, allowed_filter_cols=["initial_qty", "remaining_qty", "description", "estimated_value"], sort_cols=prize.Prize.get_lowercase_columns())
            if result == None:
                return
            
            (sql, params) = result
            for row in cursor.execute(sql, params | {"contest_id": contest_id}):
                out += [prize.Prize().from_full_tuple(row)]
        
        self.simple_response_code(200)
        self.handler.wfile.write(bytes(json.dumps(out, default=lambda x: x.as_dict()), "UTF-8"))
        self.handler.wfile.flush()

    def post_prize(self, contest_id: int):
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

            if req["contest_id"] != contest_id:
                self.simple_response_code(422)
                self.output_error(Exception("Contest ID may not be different between path and request"))
                return

        if "description" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing description"))
            return
        if "photo_data" not in req or req["photo_data"] is None:
            req["photo_data"] = json.dumps(None)
        if "initial_qty" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing initial quantity"))
            return
        else:
            req["initial_qty"] = self.convert_numeric_or_code(req["initial_qty"], 400)
            if req["initial_qty"] == None:
                self.output_error(Exception("Invalid initial quantity"))

        if "estimated_value" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing estimated value"))
            return
        else:
            req["estimated_value"] = self.convert_numeric_or_code(req["estimated_value"], 400)
            if req["estimated_value"] == None:
                self.output_error(Exception("Invalid estimated value"))
    
        if "prize_id" in req:
            self.simple_response_code(422)
            self.output_error(Exception("Prize ID may not be set"))
            return
        if "remaining_qty" in req:
            self.simple_response_code(422)
            self.output_error(Exception("Remaining quantity may not be set"))
            return

        if len({col.lower() for col in req.keys()} - set(prize.Prize.get_lowercase_columns())) > 0:
            self.simple_response_code(422)
            self.output_error(Exception("Invalid members in request"))
            return
        
        with DBConnection() as conn, conn.cursor() as cursor:
            item = get_by_id(contest.Contest, {"id": contest_id}, cursor)
            if item == None:
                self.simple_response_code(404)
                return
            
            id_var = cursor.var(int)
            params = {"contest_id": contest_id, "initial_qty": req["initial_qty"], "remaining_qty": req["initial_qty"], "description": req["description"], "estimated_value": req["estimated_value"], "photo_data": str(req["photo_data"]), "prize_id": id_var}

            try:
                cursor.execute("INSERT INTO PRIZES(contest_id, initial_qty, remaining_qty, description, estimated_value, photo_data) VALUES(:contest_id, :initial_qty, :remaining_qty, :description, :estimated_value, :photo_data) RETURNING prize_id INTO :prize_id", params)
                conn.commit()
            except oracledb.DatabaseError as e:
                print(e)
                error = e.args[0]
                result = prize.Prize.simplify_integrity_error_message(error.code, error.message)
                self.simple_response_code(result[0])
                self.output_error(Exception(result[1]))
                return

            item = get_by_id(prize.Prize, {"contest_id": contest_id, "prize_id": id_var.getvalue()[0]}, cursor)

        self.simple_response_code(201, False)
        self.handler.send_header("Location", f"/contests/{item.contest_id}/prizes/{item.prize_id}")
        self.handler.end_headers()

        self.handler.wfile.write(bytes(json.dumps(item.as_dict()), 'UTF-8'))
        self.handler.wfile.flush()
        
    def delete_prize(self, contest_id: int, prize_id: int):
        with DBConnection() as conn, conn.cursor() as cursor:
            try:
                count = delete_by_id(prize.Prize, {"contest_id": contest_id, "prize_id": prize_id}, cursor)
            except oracledb.DatabaseError as e:
                error = e.args[0]
                result = prize.Prize.simplify_integrity_error_message(error.code, error.message)
                self.simple_response_code(result[0])
                self.output_error(Exception(result[1]))
                return

            if count == 0:
                self.simple_response_code(404)
            else:
                self.simple_response_code(204)
    
    def put_prize(self, contest_id: int, prize_id: int):
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
        
        if "prize_id" in req:
            req["prize_id"] = self.convert_numeric_or_code(req["prize_id"], 400)
            if req["prize_id"] == None:
                self.output_error(Exception("Invalid prize ID"))
                return

            if req["prize_id"] != prize_id:
                self.simple_response_code(422)
                self.output_error(Exception("Prize ID may not be different between path and request"))
                return
        if "contest_id" in req:
            req["contest_id"] = self.convert_numeric_or_code(req["contest_id"], 400)
            if req["contest_id"] == None:
                self.output_error(Exception("Invalid contest ID"))
                return

            if req["contest_id"] != contest_id:
                self.simple_response_code(422)
                self.output_error(Exception("Contest ID may not be different between path and request"))
                return

        if "description" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing description"))
            return
        if "photo_data" not in req or req["photo_data"] is None:
            req["photo_data"] = json.dumps(None)

        req["photo_data"] = str(req["photo_data"])
        if "initial_qty" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing initial quantity"))
            return
        else:
            req["initial_qty"] = self.convert_numeric_or_code(req["initial_qty"], 400)
            if req["initial_qty"] == None:
                self.output_error(Exception("Invalid initial quantity"))

        if "estimated_value" not in req:
            self.simple_response_code(400)
            self.output_error(Exception("Missing estimated value"))
            return
        else:
            req["estimated_value"] = self.convert_numeric_or_code(req["estimated_value"], 400)
            if req["estimated_value"] == None:
                self.output_error(Exception("Invalid estimated value"))

        if "remaining_qty" in req:
            self.simple_response_code(422)
            self.output_error(Exception("Remaining quantity may not be set"))
            return

        if len({col.lower() for col in req.keys()} - set(prize.Prize.get_lowercase_columns())) > 0:
            self.simple_response_code(422)
            self.output_error(Exception("Invalid members in request"))
            return
        
        with DBConnection() as conn, conn.cursor() as cursor:
            item = get_by_id(contest.Contest, {"id": contest_id}, cursor)
            if item == None:
                self.simple_response_code(404)
                return
            
            try:
                count = update_by_id(prize.Prize, {"contest_id": contest_id, "prize_id": prize_id}, req, cursor)
            except oracledb.DatabaseError as e:
                error = e.args[0]
                result = prize.Prize.simplify_integrity_error_message(error.code, error.message)
                self.simple_response_code(result[0])
                self.output_error(Exception(result[1]))
                return

            if count == 0:
                self.simple_response_code(404)
                return

            item = get_by_id(prize.Prize, {"contest_id": contest_id, "prize_id": prize_id}, cursor)

        self.simple_response_code(200)

        self.handler.wfile.write(bytes(json.dumps(item.as_dict()), 'UTF-8'))
        self.handler.wfile.flush()

    def patch_prize(self, contest_id: int, prize_id: int):
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
        
        if "prize_id" in req:
            req["prize_id"] = self.convert_numeric_or_code(req["prize_id"], 400)
            if req["prize_id"] == None:
                self.output_error(Exception("Invalid prize ID"))
                return

            if req["prize_id"] != prize_id:
                self.simple_response_code(422)
                self.output_error(Exception("Prize ID may not be different between path and request"))
                return
        if "contest_id" in req:
            req["contest_id"] = self.convert_numeric_or_code(req["contest_id"], 400)
            if req["contest_id"] == None:
                self.output_error(Exception("Invalid contest ID"))
                return

            if req["contest_id"] != contest_id:
                self.simple_response_code(422)
                self.output_error(Exception("Contest ID may not be different between path and request"))
                return

        if "initial_qty" in req:
            req["initial_qty"] = self.convert_numeric_or_code(req["initial_qty"], 400)
            if req["initial_qty"] == None:
                self.output_error(Exception("Invalid initial quantity"))

        if "estimated_value" in req:
            req["estimated_value"] = self.convert_numeric_or_code(req["estimated_value"], 400)
            if req["estimated_value"] == None:
                self.output_error(Exception("Invalid estimated value"))

        if "remaining_qty" in req:
            self.simple_response_code(422)
            self.output_error(Exception("Remaining quantity may not be set"))
            return

        print(req["photo_data"])
        if "photo_data" not in req or req["photo_data"] is None:
            req["photo_data"] = json.dumps(None)

        req["photo_data"] = str(req["photo_data"])
        if len({col.lower() for col in req.keys()} - set(prize.Prize.get_lowercase_columns())) > 0:
            self.simple_response_code(422)
            self.output_error(Exception("Invalid members in request"))
            return
        
        with DBConnection() as conn, conn.cursor() as cursor:
            item = get_by_id(contest.Contest, {"id": contest_id}, cursor)
            if item == None:
                self.simple_response_code(404)
                return

            try:
                count = update_by_id(prize.Prize, {"contest_id": contest_id, "prize_id": prize_id}, req, cursor)
            except oracledb.DatabaseError as e:
                error = e.args[0]
                result = prize.Prize.simplify_integrity_error_message(error.code, error.message)
                self.simple_response_code(result[0])
                self.output_error(Exception(result[1]))
                return

            if count == 0:
                self.simple_response_code(404)
                return

            item = get_by_id(prize.Prize, {"contest_id": contest_id, "prize_id": prize_id}, cursor)

        self.simple_response_code(200)

        self.handler.wfile.write(bytes(json.dumps(item.as_dict()), 'UTF-8'))
        self.handler.wfile.flush()

    def get_single_prize(self, contest_id: int, prize_id: int):
        with DBConnection() as conn, conn.cursor() as cursor:
            item = get_by_id(prize.Prize, {"contest_id": contest_id, "prize_id": prize_id}, cursor)
        
        if item == None:
            self.simple_response_code(404)
        else:
            self.simple_response_code(200)

            self.handler.wfile.write(bytes(json.dumps(item.as_dict()), 'UTF-8'))
            self.handler.wfile.flush()
