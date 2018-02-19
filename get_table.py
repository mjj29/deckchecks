#!/usr/bin/env python
import csv, sys, cgitb, os, cgi
from deck_mysql import DeckDB
from printers import TextOutput, HTMLOutput

output = None

def print_table(tournament, tablenumber):

		with DeckDB() as db:
			id = db.getEventId(tournament)
			maxrounds = db.get_round(id)
			headers = output.getHeaders(maxrounds)

			output.createButton("deckcheck", {"table": tablenumber}, "Check table this round")

			for r in range(maxrounds, 0, -1):
				try:
					(player1, player2) = db.get_table(id, tablenumber, roundnum=r)
					output.heading("Players at table %s in round %s" % (tablenumber, r))

					with output.table(*headers):
						output.printPlayer(player1, db, id)
						output.printPlayer(player2, db, id)
					
				except Exception as e:
					output.printComment("Failed to lookup table %s in round %s: %s" % (tablenumber, r, e))

			try:
				output.heading("Players at build table %s" % tablenumber)
				players = db.get_build_table(id, tablenumber)
				with output.table(*headers):
					for player in players:
						output.printPlayer(player, db, id)
			except Exception as e:
				output.printMessage("Failed to lookup table %s: %s" % (tablenumber, e))

def docgi():
	print """Content-type: text/html

	<html>
		<head><title>Deck Checks - lookup table</title><link rel='stylesheet' href='style.css' /></head>
		<body>
			<h1>Lookup table</h1>
"""
	form = cgi.FieldStorage()
	with DeckDB() as db:
		db.checkEvent(form["event"].value, output)
		roundnum = db.get_round(db.getEventId(form["event"].value))
	output.pageHeader(form['event'].value, roundnum)
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
