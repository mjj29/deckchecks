#!/usr/bin/env python
import csv, sys, cgitb, os, cgi
from deck_mysql import DeckDB
from printers import TextOutput, HTMLOutput

output = None

def top_tables(tournament):

	try:
		with DeckDB() as db:
			id = db.getEventId(tournament)
			tables = db.get_top_tables()
			with output.table("Table", "Score", "Name", "Previous Checks", "Name", "Previous Checks") as table:
				for row in tables:
					score = row[0]
					tablenum = row[1]
					(player1, player2) = db.get_table(id, tablenum)
					(name1, _, _, _) = player1
					(name2, _, _, _) = player2
					prevChecks1 = db.getPreviousChecks(id, name1)
					prevChecks2 = db.getPreviousChecks(id, name2)
					table.printRow(tablenum, score, name1, ", ".join([str(x) for x in prevChecks1]), name2, ", ".join([str(x) for x in prevChecks2]))

	except Exception as e:
		output.printMessage("Failed to print top tables: %s" % (e))

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
	top_tables(form["event"].value)
	print """
			<p><a href='root'>Return to menu</a></p>
		</body>
	</html>
"""

def main(args):
	with DeckDB() as db:
		db.checkEvent(args[0], output)
	top_tables(args[0])

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
