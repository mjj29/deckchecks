#!/usr/bin/env python
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import csv, sys, cgitb, os, cgi
from deck_mysql import DeckDB
from printers import JSONOutput



def table(output):
    data = cgi.FieldStorage()
    with DeckDB() as db:
        db.checkEvent(data["event"].value, output)
        id = db.getEventId(data["event"].value)
        tablenum = data["arg"].value
        maxrounds = db.get_round(id)
        output.sendjson({"number":tablenum, "table":[
            {"round":round, "players":[
                    {"name":name, "score":score} for (name, score, _, _) in db.get_table(id, tablenum, round)
                ]} for round in range(maxrounds, 0, -1)
          ]+[{"round":"0", "players":[
              {"name":name, "score":score} for (name, score, _, _) in db.get_build_table(id, tablenum)
          ]}]})

if __name__ == "__main__":
    with JSONOutput() as output:
        cgitb.enable()
        table(output)

