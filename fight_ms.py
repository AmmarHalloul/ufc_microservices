from concurrent.futures import ThreadPoolExecutor
from ufc_pb2 import *
from ufc_pb2_grpc import *
import grpc
import os
import sqlite3

DB_NAME = "fights.db"
FIGHTER_STATS_URI = "localhost:50051"

class Fights(FightsServicer):

    def GetFight(self, request, context):
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            res = cur.execute('SELECT * FROM fights where name1=? or name2=?', (request.name, request.name,))
            reply = FightReply()     
            reply.fights.extend([Fight(id=l[0], name1=l[1], name2=l[2], winner=l[3], won_by=l[4]) for l in res.fetchall()])
            return reply
    
    def GetAllFights(self, request, context):
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            res = cur.execute('SELECT * FROM fights')
            reply = FightReply()     
            reply.fights.extend([Fight(id=l[0], name1=l[1], name2=l[2], winner=l[3], won_by=l[4]) for l in res.fetchall()])
            return reply

    def AddFight(self, request, context):
        with grpc.insecure_channel(FIGHTER_STATS_URI) as channel: 
            stub = FighterStatsStub(channel)
            stub.FightAdded(MinimalFight(name1=request.name1, name2=request.name2, winner=request.winner))    

        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            res = cur.execute('INSERT INTO fights (name1, name2, winner, won_by) VALUES (?, ?, ?, ?)', 
                              (request.name1, request.name2, request.winner, request.won_by,))
            reply = AddFightReply(id=cur.lastrowid)
            con.commit()

            return reply
        
    def RemoveFight(self, request, context):
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("SELECT name1, name2, winner FROM fights WHERE id = ?", (request.id,))
            deleted_row = cur.fetchone()
            cur.execute('DELETE FROM fights WHERE id=?', (request.id,))
            reply = RemoveFightReply(removed=cur.rowcount)
            con.commit()

            if deleted_row:
                with grpc.insecure_channel(FIGHTER_STATS_URI) as channel: 
                    stub = FighterStatsStub(channel)
                    stub.FightRemoved(MinimalFight(name1=deleted_row[0], name2=deleted_row[1], winner=deleted_row[2])) 

            return reply

def serve():    
    if not os.path.exists(DB_NAME):
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE fights (
                id INTEGER PRIMARY KEY ,
                name1 TEXT ,
                name2 TEXT,
                winner INTEGER ,
                won_by TEXT
            )""")
        con.commit()
        
    
    server = grpc.server(ThreadPoolExecutor(max_workers=8))
    add_FightsServicer_to_server(Fights(), server)
    server.add_insecure_port('localhost:50052')
    server.start()
    print("Server started, listening on port 50052..")
    server.wait_for_termination()


if __name__ == "__main__": 
    serve()