#!/usr/bin/env python
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

import csv, sys, cgitb, os, cgi
from deck_mysql import DeckDB
from printers import TextOutput, HTMLOutput
from login import check_login

output = None

def pairings(tournament, roundnum=None):

	try:
		with DeckDB() as db:
			id = db.getEventId(tournament)
			pairings = db.get_pairings(id, roundnum)
			with output.table("Table", "Name", "Score", "Name", "Score") as table:
				for row in pairings:
					try:
						table.printRow(*row)
					except:
						pass

	except Exception as e:
		output.printMessage("Failed to print pairings: %s" % (e))

def docgi():
	print """Content-type: text/html

	<html>
		<head><title>Pairings</title><link rel='stylesheet' href='style.css' /></head>
		<body>
""" 
	form = cgi.FieldStorage()
	with DeckDB() as db:
		db.checkEvent(form["event"].value, output)
		hasPairings = db.hasEventPairings(db.getEventId(form["event"].value))
		if not hasPairings: raise Exception("Pairings not enabled for this event")
		maxrounds = db.get_round(db.getEventId(form["event"].value))
		roundnum = int(form['round'].value) if 'round' in form else maxrounds
		print "<h1>Pairings for %s round %s</h1>" % (db.getEventName(form['event'].value), roundnum)
	print '<div class="links">|'
	for i in range(1, maxrounds+1):
		print output.makeLink(form, 'pairings?round=%s'%i, str(i))
		print '|'
	print '</div>'
	pairings(form["event"].value, roundnum)
	print """
		</body>
	</html>
"""

def main(args):
	with DeckDB() as db:
		db.checkEvent(args[0], output)
	pairings(args[0], {})

if __name__ == "__main__":

	if 'REQUEST_URI' in os.environ:
		cgitb.enable()
		output = HTMLOutput()
		docgi()
	else:
		if len(sys.argv) < 2:
			print "Usage: top_tables.py <event>"
			sys.exit(1)
		
		output = TextOutput()
		main(sys.argv[1:])
