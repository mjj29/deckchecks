#!/usr/bin/env python
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import csv, sys, cgitb, os, cgi
from deck_mysql import DeckDB
from printers import JSONOutput



def player(output):
    data = cgi.FieldStorage()
    with DeckDB() as db:
        db.checkEvent(data["event"].value, output)
        id = db.getEventId(data["event"].value)
        maxrounds = db.get_round(id)
        namefragment = data["arg"].value
        output.sendjson({"players":[
           {"name":name, "score":score, "buildtable":buildtable, "checks":db.getPreviousChecks(id, name),
            "listid":"", "tables":tables
            } for (name, score, tables, buildtable) in db.get_players(id, namefragment)
          ]})

if __name__ == "__main__":
    with JSONOutput() as output:
        cgitb.enable()
        player(output)


