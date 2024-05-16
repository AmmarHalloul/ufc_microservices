from concurrent.futures import ThreadPoolExecutor
from ufc_pb2 import *
from ufc_pb2_grpc import *
import grpc
import os
import sqlite3

DB_NAME = "fighter_stats.db"

       

class FighterStats(FighterStatsServicer):

    def GetFighter(self, request, context):
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            res = cur.execute('SELECT * FROM fighter_stats WHERE name=?', (request.name,))
            l = res.fetchone()
            if l is None:
                return None
            
            f = Fighter(name=l[0], wins=l[1], losses=l[2], no_contest=l[3])
            return FighterReply(fighter=f)
    
    def GetAllFighters(self, request, context):
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            res = cur.execute('SELECT * FROM fighter_stats')
            reply = AllFighterReply()

            reply.fighters.extend([Fighter(name=l[0], wins=l[1], losses=l[2], no_contest=l[3]) for l in res.fetchall()])
            return reply
    
    def FightAdded(self, request, context):
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            added = 0
            def fighter_increment(name, column):
                cur.execute(f"UPDATE fighter_stats SET {column} = {column} + 1 WHERE name = ?",
                            (name,))
                if cur.rowcount == 0:
                    cur.execute(f"INSERT INTO fighter_stats (name, {column}) VALUES (?, 1)",
                                (name,))
                    nonlocal added
                    added += 1
                con.commit()
                
                

            if request.winner == 0:
                fighter_increment(request.name1, "no_contest")
                fighter_increment(request.name2, "no_contest")
            elif request.winner == 1:
                fighter_increment(request.name1, "wins")
                fighter_increment(request.name2, "losses")
            elif request.winner == 2:
                fighter_increment(request.name1, "losses")
                fighter_increment(request.name2, "wins")
            else:
                return None


            return FighterChangeReply(added=added)
    
    def FightRemoved(self, request, context):
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            def fighter_decrement(name, column):
                cur.execute(f"UPDATE fighter_stats SET {column} = {column} - 1 WHERE name = ?",
                            (name,))
                con.commit()
                
                    
            if request.winner == 0:
                fighter_decrement(request.name1, "no_contest")
                fighter_decrement(request.name2, "no_contest")
            elif request.winner == 1:
                fighter_decrement(request.name1, "wins")
                fighter_decrement(request.name2, "losses")
            elif request.winner == 2:
                fighter_decrement(request.name1, "losses")
                fighter_decrement(request.name2, "wins")
            else:
                return None

            return FighterChangeReply(added=0)


def serve():    
    if not os.path.exists(DB_NAME):
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE fighter_stats (
                name TEXT PRIMARY KEY UNIQUE,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                no_contest INTEGER DEFAULT 0
            )""")
        con.commit()
        
    
    server = grpc.server(ThreadPoolExecutor(max_workers=8))
    add_FighterStatsServicer_to_server(FighterStats(), server)
    server.add_insecure_port('localhost:50051')
    server.start()
    print("Server started, listening on port 50051...")
    server.wait_for_termination()


if __name__ == "__main__": 
    serve()