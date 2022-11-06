#!/usr/bin/env python
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
from deck_mysql import DeckDB
from printers import JSONOutput
import csv, sys, os, cgi, cgitb


def pairings(output):
    data = cgi.FieldStorage()
    with DeckDB() as db:
        db.checkEvent(data["event"].value, output)
        id = db.getEventId(data["event"].value)
        roundnum = data["arg"].value
        output.sendjson({"round":roundnum, "pairings":[
            {"table":row[0], "players":[{"name":row[1], "score":row[2]}, {"name":row[3], "score":row[4]}]} for row in db.get_pairings(id, roundnum)
        ]})

if __name__ == "__main__":
    with JSONOutput() as output:
        cgitb.enable()
        pairings(output)

