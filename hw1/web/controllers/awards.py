import json

from . import BaseController
from models import award, contestant
from util.database import DBConnection, get_by_id, update_by_id, delete_by_id

class AwardsController(BaseController):
    def get_awards(self, contestant_id: int, query_dict: dict[str, list[str]]):
        out = []
        with DBConnection() as conn, conn.cursor() as cursor:
            item = get_by_id(contestant.Contestant, {"id": contestant_id}, cursor)
            if item == None:
                self.simple_response_code(404)
                return

            sql = f"select {', '.join(award.Award.get_lowercase_columns())} from {award.Award.get_table_name()} where contestant_id = :contestant_id"
            result = self.prepare_sql_pagination_filtering_or_bad_req(sql, query_dict, allowed_filter_cols=["contest_id"], sort_cols=award.Award.get_lowercase_columns())
            if result == None:
                return
            
            (sql, params) = result
            for row in cursor.execute(sql, params | {"contestant_id": contestant_id}):
                out += [award.Award().from_full_tuple(row)]
        
        self.simple_response_code(200)
        self.handler.wfile.write(bytes(json.dumps(out, default=lambda x: x.as_dict()), "UTF-8"))
        self.handler.wfile.flush()

    def get_single_award(self, prize_id: int, contestant_id: int):
        with DBConnection() as conn, conn.cursor() as cursor:
            item = get_by_id(award.Award, {"prize_id": prize_id, "contestant_id": contestant_id}, cursor)
        
        if item == None:
            self.simple_response_code(404)
        else:
            self.simple_response_code(200)

            self.handler.wfile.write(bytes(json.dumps(item.as_dict()), 'UTF-8'))
            self.handler.wfile.flush()
