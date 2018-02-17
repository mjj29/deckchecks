#!/usr/bin/env python
import csv, sys, cgitb, os, cgi
from deck_mysql import DeckDB
from printers import TextOutput, HTMLOutput

output = None

def print_table(tournament, tablenumber):

		with DeckDB() as db:
			id = db.getEventId(tournament)
			try:
				(player1, player2) = db.get_table(id, tablenumber)

				with output.table("Name", "Score", "Current Table", "Build Table", "Previous Checks", "Check this round"):
					output.printPlayer(player1, db, id)
					output.printPlayer(player2, db, id)
				
				output.printLink("deckcheck?table=%s" % tablenumber, "Mark table as checked")
			except Exception as e:
				output.printMessage("Failed to lookup table %s: %s" % (tablenumber, e))

			try:
				players = db.get_build_table(id, tablenumber)
				with output.table("Name", "Score", "Current Table", "Build Table", "Previous Checks", "Check this round"):
					for player in players:
						output.printPlayer(player, db, id)
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
		print_table(form["event"].value, int(form["table"].value))
	else:
		print """
<form>
	Enter table number: <input type='text' name='table' /><input type='submit' />
</form>
"""

	print """
			<p><a href='root'>Return to menu</a></p>
		</body>
	</html>
"""

def main(args):
	with DeckDB() as db:
		db.checkEvent(args[0], output)
	print_table(args[0], args[1])

if __name__ == "__main__":

	if 'REQUEST_URI' in os.environ:
		cgitb.enable()
		output = HTMLOutput()
		docgi()
	else:
		if len(sys.argv) < 3:
			print "Usage: get_table.py <event> <table number>"
			sys.exit(1)
		
		output = TextOutput()
		main(sys.argv[1:])
