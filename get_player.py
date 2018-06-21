#!/usr/bin/env python
import csv, sys, cgitb, os, cgi
from deck_mysql import DeckDB
from printers import TextOutput, HTMLOutput
from login import check_login

output = None

def print_player(event, name, form):

	try:
		with DeckDB() as db:
			id = db.getEventId(event)
			players = db.get_players(id, name)
			maxrounds = db.get_round(id)

			headers = output.getHeaders(maxrounds)

			with output.table(*headers):
				for player in players:
					output.printPlayer(player, db, id, form)
	except Exception as e:
		output.printMessage("Failed to lookup player %s: %s" % (name, e))


def docgi():
			
	print """Content-type: text/html

	<html>
		<head><title>Deck Checks - lookup player</title><link rel='stylesheet' href='style.css' /></head>
		<body>
			<h1>Lookup player</h1>
"""
	form = cgi.FieldStorage()
	with DeckDB() as db:
		db.checkEvent(form["event"].value, output)
		roundnum = db.get_round(db.getEventId(form["event"].value))
		output.pageHeader(db, form['event'].value, roundnum, form)
	if not check_login(output, form['event'].value, form['password'].value if 'password' in form else '', 'get_player'):
		return
	if "name" in form:
		print_player(form["event"].value, form["name"].value, form)
	else:
		print """
<form>
	<input type='hidden' name='password' value='%s'/>
	Enter name: <input type='text' name='name' /><input type='submit' />
</form>
<p>
You can enter any fragment of a name, all matches will be returned. Searches are case-insensitive. Typos will not match.
</p>
"""%form['password'].value if 'password' in form else ''

	output.printLink(form, 'root', 'Return to menu')
	print """
		</body>
	</html>
"""

def main(args):
	with DeckDB() as db:
		db.checkEvent(args[0], output)
	print_player(args[0], " ".join(args[1:]), {})

if __name__ == "__main__":

	if 'REQUEST_URI' in os.environ:
		cgitb.enable()
		output = HTMLOutput()
		docgi()
	else:
		if len(sys.argv) < 3:
			print "Usage: get_player.py <event> <player name>"
			sys.exit(1)
		
		output = TextOutput()
		main(sys.argv[1:])
