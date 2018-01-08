#!/usr/bin/env python
import csv, sys, cgitb, os, cgi
from deck_mysql import DeckDB
from printers import TextOutput, HTMLOutput

output = None

def print_player(name):

	with DeckDB() as db:
		players = db.get_players(name)

	with output.table("Name", "Score", "Build Table"):
		for player in players:
			output.printPlayer(player)


def docgi():
	print """Content-type: text/html

	<html>
		<head><title>Deck Checks</title></head>
		<body>
			<h1>Deck Checks</h1>
"""
	form = cgi.FieldStorage()
	if "name" in form:
		print_player(form["name"].value)
	else:
		print """
<form>
	Enter name: <input type='text' name='name' /><input type='submit' />
</form>
"""

	print """
		</body>
	</html>
"""

def main(args):
	print_player(" ".join(args))

if __name__ == "__main__":

	if 'REQUEST_URI' in os.environ:
		cgitb.enable()
		output = HTMLOutput()
		docgi()
	else:
		if len(sys.argv) < 2:
			print "Usage: get_player.py <player name>"
			sys.exit(1)
		
		output = TextOutput()
		main(sys.argv[1:])
