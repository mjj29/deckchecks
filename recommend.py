#!/usr/bin/env python
import csv, sys, cgitb, os, cgi
from deck_mysql import DeckDB
from printers import TextOutput, HTMLOutput

output = None

def recommend_checks(tournament):
	try:
		with DeckDB() as db:
			id = db.getEventId(tournament)
			tables = db.get_recommendations(id)
			for (tablenumber, player1, player2) in tables:
				output.heading("Table %s"%tablenumber)
				with output.table("Name", "Score", "Current Table", "Build Table", "Previous Checks"):
					output.printPlayer(player1, db, id)
					output.printPlayer(player2, db, id)
			
				output.printLink("deckcheck?table=%s" % tablenumber, "Mark as checked")

	except Exception as e:
		output.printMessage("Failed to print recommendations: %s" % (e))

def docgi():
	print """Content-type: text/html

	<html>
		<head><title>Deck Checks</title></head>
		<body>
			<h1>Deck Checks</h1>
"""
	form = cgi.FieldStorage()
	with DeckDB() as db:
		db.checkEvent(form["event"].value, output)
	output.printMessage("Tournament is %s" % form["event"].value)
	try:
		with DeckDB() as db:
			id = db.getEventId(form["event"].value)
			roundnum = db.get_round(id)
			output.printMessage("Current round is %s" % roundnum)
	except Exception as e:
		output.printMessage("Failed to get round number: %s" % e)
	recommend_checks(form["event"].value)
	print """
		<p>
			Note: recommendations are currently completely random
		</p>
			<p><a href='root'>Return to menu</a></p>
		</body>
	</html>
"""

def main(args):
	with DeckDB() as db:
		db.checkEvent(args[0], output)
	recommend_checks(args[0])

if __name__ == "__main__":

	if 'REQUEST_URI' in os.environ:
		cgitb.enable()
		output = HTMLOutput()
		docgi()
	else:
		if len(sys.argv) < 2:
			print "Usage: recommend.py <event>"
			sys.exit(1)
		
		output = TextOutput()
		main(sys.argv[1:])
