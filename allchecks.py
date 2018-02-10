#!/usr/bin/env python
import csv, sys, cgitb, os, cgi
from deck_mysql import DeckDB
from printers import TextOutput, HTMLOutput

output = None

def allchecks(tournament):

	try:
		with DeckDB() as db:
			id = db.getEventId(tournament)
			checks = db.get_all_checks(id)
			for rn in sorted(checks.keys()):
				output.heading("Round %s"%rn)
				with output.table("Name") as table:
					for name in checks[rn]:
						table.printRow(name)

	except Exception as e:
		output.printMessage("Failed to print check history: %s" % (e))

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
	allchecks(form["event"].value)
	print """
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
