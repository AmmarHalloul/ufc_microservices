from flask import Flask, request, jsonify
from ufc_pb2 import *
from ufc_pb2_grpc import *
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


@app.get("/fighters")
def get_fighters():
    with grpc.insecure_channel(FIGHTER_STATS_URI) as channel: 
        stub = FighterStatsStub(channel)
        res = stub.GetAllFighters(AllFighterRequest())
        data = []
        for i in res.fighters:
            data.append({
                "name": i.name, 
                "wins": i.wins,
                "losses": i.losses,
                "no_contest": i.no_contest,
            })
        
        return jsonify(data)


@app.get("/fight/<name>")
def get_fight(name):
    with grpc.insecure_channel(FIGHTS_URI) as channel: 
        stub = FightsStub(channel)
        res = stub.GetFight(FightRequest(name=name))
        data = []
        for i in res.fights:
            data.append({
                "id": i.id, 
                "name1": i.name1,
                "name2": i.name2,
                "winner": i.winner,
                "won_by": i.won_by,
            })
        
        return jsonify(data)

@app.get("/fights")
def get_all_fights():
    with grpc.insecure_channel(FIGHTS_URI) as channel: 
        stub = FightsStub(channel)
        res = stub.GetAllFights(AllFightsRequest())
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
    with grpc.insecure_channel(FIGHTS_URI) as channel: 
        stub = FightsStub(channel)
        req = request.get_json()
        res = stub.AddFight(AddFightRequest(name1=req['name1'], name2=req['name2'], winner=req['winner'], won_by=req['won_by']))
        data = {"id": res.id}
        return jsonify(data)

@app.delete("/fight/<id>")
def delete_fight(id):
    with grpc.insecure_channel(FIGHTS_URI) as channel: 
        stub = FightsStub(channel)
        res = stub.RemoveFight(RemoveFightRequest(id=int(id)))
        data = {"removed": res.removed}
        return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)

