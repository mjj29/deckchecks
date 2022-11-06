#!/usr/bin/env python
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import csv, sys, cgitb, os, cgi
from deck_mysql import DeckDB
from printers import JSONOutput

def list(output):
    data = cgi.FieldStorage()
    with DeckDB() as db:
        db.checkEvent(data["event"].value, output)
        id = db.getEventId(data["event"].value)
        uuid = data["arg"].value
        #TODO
        raise Exception("Deck list not found with id "+uuid)
        output.sendjson({"main":[], "side":[]})

if __name__ == "__main__":
    with JSONOutput() as output:
        cgitb.enable()
        list(output)
