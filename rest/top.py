#!/usr/bin/env python
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import csv, sys, cgitb, os, cgi
from deck_mysql import DeckDB
from printers import JSONOutput
from swisscalc import calculateTop8Threshold



def top(output):
    data = cgi.FieldStorage()
    with DeckDB() as db:
        db.checkEvent(data["event"].value, output)
        id = db.getEventId(data["event"].value)
        currentRound = db.get_round(id)
        totalRounds = db.getEventRounds(id)
        playersWithEachByes = db.getPlayersForEachByeNumber(id)

        (currentMarginalThreshold, currentTop8Threshold, undefeatedThreshold) = calculateTop8Threshold(playersWithEachByes, totalRounds, currentRound)

        toptables=[]
        tables = db.get_top_tables(id)
        for row in tables:
            score = row[0]
            tablenum = row[1]
            maxscore = max([score for (_, score, _, _) in db.get_table(id, tablenum)])
            state=""
            if maxscore == undefeatedThreshold:
               state='undefeated'
            elif maxscore < currentMarginalThreshold:
               state='dead'
            elif maxscore >= currentTop8Threshold:
               state='live'
            elif maxscore > currentMarginalThreshold:
               state='marginal'
            else:
               state='unlikely'
            toptables.append({"number":tablenum, "livestatus":state, "players":[
               {"name":name, "score":score, "checks":db.getPreviousChecks(id, name)} for (name, score, _, _) in db.get_table(id, tablenum)
            ]})

        output.sendjson({"threshold":currentTop8Threshold,"top":toptables})

if __name__ == "__main__":
    with JSONOutput() as output:
        cgitb.enable()
        top(output)
