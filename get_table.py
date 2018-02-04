#!/usr/bin/env python
import csv, sys, cgitb, os, cgi
from deck_mysql import DeckDB
from printers import TextOutput, HTMLOutput

output = None

def print_table(tablenumber):

	try:
		with DeckDB() as db:
			(player1, player2) = db.get_table(tablenumber)

		with output.table("Name", "Score", "Current Table", "Build Table"):
			output.printPlayer(player1)
			output.printPlayer(player2)
	except Exception as e:
		output.printMessage("Failed to lookup table %s: %s" % (tablenumber, e))

def docgi():
	print """Content-type: text/html

	<html>
		<head><title>Deck Checks</title></head>
		<body>
			<h1>Deck Checks</h1>
"""
	try:
		with DeckDB() as db:
			roundnum = db.get_round()
			output.printMessage("Current round is %s" % roundnum)
	except Exception as e:
		output.printMessage("Failed to get round number: %s" % e)
	form = cgi.FieldStorage()
	if "table" in form:
		print_table(int(form["table"].value))
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
	print_table(args[0])

if __name__ == "__main__":

	if 'REQUEST_URI' in os.environ:
		cgitb.enable()
		output = HTMLOutput()
		docgi()
	else:
		if len(sys.argv) < 2:
			print "Usage: get_table.py <table number>"
			sys.exit(1)
		
		output = TextOutput()
		main(sys.argv[1:])
