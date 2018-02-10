#!/usr/bin/env python
import csv, sys, cgitb, os, cgi
from deck_mysql import DeckDB
from printers import TextOutput, HTMLOutput

output = None

def mark_checked(tournament, tablenumber):

	try:
		with DeckDB() as db:
			id = db.getEventId(tournament)
			(player1, player2) = db.get_table_ids(id, tablenumber)
			round = db.get_round(id)
			db.insert('deckchecks', [player1, id, round])
			db.insert('deckchecks', [player2, id, round])

		output.printMessage("Marked table %s as checked in round %s" % (tablenumber, round))
	except Exception as e:
		output.printMessage("Failed to lookup table %s: %s" % (tablenumber, e))

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
	if "table" in form:
		mark_checked(form["event"].value, int(form["table"].value))
	else:
		print """
<form>
	Enter table number: <input type='text' name='table' /><input type='submit' />
</form>
"""

	print """
		</body>
	</html>
"""

def main(args):
	with DeckDB() as db:
		db.checkEvent(args[0], output)
	mark_checked(args[0], int(args[1]))

if __name__ == "__main__":

	if 'REQUEST_URI' in os.environ:
		cgitb.enable()
		output = HTMLOutput()
		docgi()
	else:
		if len(sys.argv) < 3:
			print "Usage: deckcheck.py <event> <table number>"
			sys.exit(1)
		
		output = TextOutput()
		main(sys.argv[1:])
