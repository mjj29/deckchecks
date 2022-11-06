#!/usr/bin/env python
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import csv, sys, cgitb, os, cgi
from deck_mysql import DeckDB
from printers import JSONOutput

def lists(output):
    data = cgi.FieldStorage()
    with DeckDB() as db:
        db.checkEvent(data["event"].value, output)
        id = db.getEventId(data["event"].value)
        #TODO
        output.sendjson({"lists":[]})

if __name__ == "__main__":
    with JSONOutput() as output:
        cgitb.enable()
        lists(output)
