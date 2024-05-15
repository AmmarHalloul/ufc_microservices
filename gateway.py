from flask import Flask, request, jsonify
from proto.ufc_pb2 import *
from proto.ufc_pb2_grpc import *
import grpc

app = Flask(__name__)
FIGHTER_STATS_URI = "localhost:50051"
FIGHTS_URI = "localhost:50052"


@app.get("/fighter/<name>")
def get_fighter(name):
    with grpc.insecure_channel(FIGHTER_STATS_URI) as channel: 
        stub = FighterStatsStub(channel)
        res = stub.GetFighter(FighterRequest(name=name))
        data = {
            "name": res.fighter.name, 
            "wins": res.fighter.wins,
            "losses": res.fighter.losses,
            "no_contest": res.fighter.no_contest,
        }
        
        return jsonify(data)


@app.get("/fight/<name>")
def get_fight(name):
    with grpc.insecure_channel(FIGHTS_URI) as channel: 
        stub = FightsStub(channel)
        res = stub.GetFight(FightRequest(name=name))
        data = []
        for i in res.fights:
            data.append({
                "id": res.fight.id, 
                "name1": res.fight.name1,
                "name2": res.fight.name2,
                "winner": res.fight.winner,
                "won_by": res.fight.won_by,
            })
        
        return jsonify(data)



@app.post("/fight")
def add_fight():
    data = request.get_json()

