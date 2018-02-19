#!/usr/bin/env python
import csv, sys, cgitb, os, cgi
from deck_mysql import DeckDB
from printers import TextOutput, HTMLOutput

output = None

def allchecks(tournament):

	try:
		with DeckDB() as db:
			id = db.getEventId(tournament)
			maxrounds = db.get_round(id)

			headers = output.getHeaders(maxrounds)

			checks = db.get_all_checks(id)
			for rn in sorted(checks.keys()):
				output.heading("Round %s"%rn)
				with output.table(*headers) as table:
					for name in checks[rn]:
						players = db.get_players(id, name)
						for p in players:
								output.printPlayer(p, db, id)

	except Exception as e:
		output.printMessage("Failed to print check history: %s" % (e))

def docgi():
	print """Content-type: text/html

	<html>
		<head><title>Deck Checks - check history</title><link rel='stylesheet' href='style.css' /></head>
		<body>
			<h1>History of checks</h1>
"""
	form = cgi.FieldStorage()
	with DeckDB() as db:
		db.checkEvent(form["event"].value, output)
		roundnum = db.get_round(db.getEventId(form["event"].value))
	output.pageHeader(form['event'].value, roundnum)
	allchecks(form["event"].value)
	print """
			<p><a href='root'>Return to menu</a></p>
		</body>
	</html>
"""

def main(args):
	with DeckDB() as db:
		db.checkEvent(args[0], output)
	allchecks(args[0])

if __name__ == "__main__":

	if 'REQUEST_URI' in os.environ:
		cgitb.enable()
		output = HTMLOutput()
		docgi()
	else:
		if len(sys.argv) < 2:
			print "Usage: allchecks.py <event>"
			sys.exit(1)
		
		output = TextOutput()
		main(sys.argv[1:])
