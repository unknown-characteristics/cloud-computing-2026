import json
import oracledb

from . import BaseController
from models import participation
from util.database import DBConnection, get_by_id, update_by_id, delete_by_id

class ParticipationsController(BaseController):
    def delete_participation(self, contest_id: int, contestant_id: int):
        with DBConnection() as conn, conn.cursor() as cursor:
            count = delete_by_id(participation.Participation, {"contest_id": contest_id, "contestant_id": contestant_id}, cursor)

            if count == 0:
                self.simple_response_code(404)
            else:
                self.simple_response_code(204)
    
    def put_participation(self, contest_id: int, contestant_id: int):
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
        

        if "contestant_id" in req:
            req["contestant_id"] = self.convert_numeric_or_code(req["contestant_id"], 400)
            if req["contestant_id"] == None:
                self.output_error(Exception("Invalid contestant ID"))
                return
            
            if req["contestant_id"] != contestant_id:
                self.simple_response_code(400)
                self.output_error(Exception("Contestant ID may not be different between path and request"))
                return
        if "contest_id" in req:
            req["contest_id"] = self.convert_numeric_or_code(req["contest_id"], 400)
            if req["contest_id"] == None:
                self.output_error(Exception("Invalid contest ID"))
                return

            if req["contest_id"] != contest_id:
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
            try:
                count = update_by_id(participation.Participation, {"contest_id": contest_id, "contestant_id": contestant_id}, req, cursor)
            except oracledb.DatabaseError as e:
                error = e.args[0]
                self.simple_response_code(409)
                self.output_error(Exception(participation.Participation.simplify_integrity_error_message(error.code, error.message)))
                return

            if count == 0:
                self.simple_response_code(404)
                return

            item = get_by_id(participation.Participation, {"contest_id": contest_id, "contestant_id": contestant_id}, cursor)

        self.simple_response_code(200)

        self.handler.wfile.write(bytes(json.dumps(item.as_dict()), 'UTF-8'))
        self.handler.wfile.flush()

    def patch_participation(self, contest_id: int, contestant_id: int):
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
        
        if "contestant_id" in req:
            req["contestant_id"] = self.convert_numeric_or_code(req["contestant_id"], 400)
            if req["contestant_id"] == None:
                self.output_error(Exception("Invalid contestant ID"))
                return

            if req["contestant_id"] != contestant_id:
                self.simple_response_code(400)
                self.output_error(Exception("Contestant ID may not be different between path and request"))
                return
        if "contest_id" in req:
            req["contest_id"] = self.convert_numeric_or_code(req["contest_id"], 400)
            if req["contest_id"] == None:
                self.output_error(Exception("Invalid contest ID"))
                return

            if req["contest_id"] != contest_id:
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
            try:
                count = update_by_id(participation.Participation, {"contest_id": contest_id, "contestant_id": contestant_id}, req, cursor)
            except oracledb.DatabaseError as e:
                error = e.args[0]
                self.simple_response_code(409)
                self.output_error(Exception(participation.Participation.simplify_integrity_error_message(error.code, error.message)))
                return

            if count == 0:
                self.simple_response_code(404)
                return

            item = get_by_id(participation.Participation, {"contest_id": contest_id, "contestant_id": contestant_id}, cursor)

        self.simple_response_code(200)

        self.handler.wfile.write(bytes(json.dumps(item.as_dict()), 'UTF-8'))
        self.handler.wfile.flush()

    def get_single_participation(self, contest_id: int, contestant_id: int):
        with DBConnection() as conn, conn.cursor() as cursor:
            item = get_by_id(participation.Participation, {"contest_id": contest_id, "contestant_id": contestant_id}, cursor)
        
        if item == None:
            self.simple_response_code(404)
        else:
            self.simple_response_code(200)

            self.handler.wfile.write(bytes(json.dumps(item.as_dict()), 'UTF-8'))
            self.handler.wfile.flush()
