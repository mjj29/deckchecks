#!/usr/bin/env python
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import csv, sys, cgitb, os, cgi
from deck_mysql import DeckDB
from printers import JSONOutput

def checks(output):
    data = cgi.FieldStorage()
    with DeckDB() as db:
        db.checkEvent(data["event"].value, output)
        id = db.getEventId(data["event"].value)
        checks = db.get_all_checks(id)
        total_names=set()
        for rn in checks.keys():
           total_names = total_names | set([name for (name, seat) in checks[rn]])

        output.sendjson({"totalchecked":len(total_names), "checks":[
           {"round":roundnum, "players":[
              name for (name, _) in checks[roundnum]
           ]} for roundnum in checks.keys()
        ]})

if __name__ == "__main__":
    with JSONOutput() as output:
        cgitb.enable()
        checks(output)
