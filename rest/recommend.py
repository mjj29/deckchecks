#!/usr/bin/env python
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import csv, sys, cgitb, os, cgi
from deck_mysql import DeckDB
from printers import JSONOutput

def recommend(output):
    data = cgi.FieldStorage()
    with DeckDB() as db:
        db.checkEvent(data["event"].value, output)
        id = db.getEventId(data["event"].value)

        output.sendjson({"recommendations":[
           {"table":tablenum, "players":[
              {"name":name, "score":score, "checks":db.getPreviousChecks(id, name)} for (name, score, _, _) in [p1, p2]
           ]} for (tablenum, p1, p2) in db.get_recommendations(id, n=6, rand=False)
        ],"random":[
           {"table":tablenum, "players":[
              {"name":name, "score":score, "checks":db.getPreviousChecks(id, name)} for (name, score, _, _) in [p1, p2]
           ]} for (tablenum, p1, p2) in db.get_recommendations(id, n=4, rand=True)
        ]})

if __name__ == "__main__":
    with JSONOutput() as output:
        cgitb.enable()
        recommend(output)
