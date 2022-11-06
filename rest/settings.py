#!/usr/bin/env python
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
from deck_mysql import DeckDB
from printers import JSONOutput
import csv, sys, os, cgi, cgitb


def settings(output):
    data = cgi.FieldStorage()
    with DeckDB() as db:
        db.checkEvent(data["event"].value, output)
        id = db.getEventId(data["event"].value)
        (name, url, rounds, password, pairings, team, decklisturl) = db.getEventSettings(id)
		  output.sendjson({"id":id, "name":name, "rounds":rounds, "pairings":bool(pairings), "team":bool(team), "decklists":False, "format":"Freeform"})

if __name__ == "__main__":
    with JSONOutput() as output:
        cgitb.enable()
        settings(output)
