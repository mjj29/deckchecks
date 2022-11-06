#!/usr/bin/env python
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import csv, sys, cgitb, os, cgi
from deck_mysql import DeckDB
from printers import JSONOutput

def missing(output):
    data = cgi.FieldStorage()
    with DeckDB() as db:
       db.checkEvent(data["event"].value, output)
       id = db.getEventId(data["event"].value)
       online = set() # TODO

       records = db.getAllPlayers(id)
       tables = {}
       for (name, buildtable) in records:
         tables[name.lower().strip()] = (name, buildtable)
       players = set([name.lower().strip() for (name, buildtable) in records])
       paperLists = players-online
       extraLists = online-players

       paperTables = {}
       for player in paperLists:
            (name, buildtable) = tables[player]
            paperTables[name] = buildtable

       output.sendjson({"missing":[
            {"name":name, "table":table} for (name, table) in paperTables.iteritems()
            ],
         "extra":[name for name in extraLists]})

if __name__ == "__main__":
    with JSONOutput() as output:
        cgitb.enable()
        missing(output)

