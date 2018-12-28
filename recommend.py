#!/usr/bin/env python
import csv, sys, cgitb, os, cgi
from deck_mysql import DeckDB
from printers import TextOutput, HTMLOutput
from login import check_login

output = None

def recommend_checks(tournament, form):
	try:
		with DeckDB() as db:
			id = db.getEventId(tournament)
			tables = db.get_recommendations(id)
			maxrounds = db.get_round(id)
			headers = output.getHeaders(maxrounds)
			for (tablenumber, player1, player2) in tables:
				output.heading("Table %s"%tablenumber)
				if db.isEventTeam(tournament):
					output.createButton(form, "deckcheck", {"table":tablenumber, 'seat':'0'}, "Checked Seat A this round")
					output.createButton(form, "deckcheck", {"table":tablenumber, 'seat':'1'}, "Checked Seat B this round")
					output.createButton(form, "deckcheck", {"table":tablenumber, 'seat':'2'}, "Checked Seat C this round")
				else:
					output.createButton(form, "deckcheck", {"table":tablenumber}, "Checked this round")
				with output.table(*headers):
					output.printPlayer(player1, db, id, form)
					output.printPlayer(player2, db, id, form)
			

	except Exception as e:
		output.printMessage("Failed to print recommendations: %s" % (e))

def docgi():
	print """Content-type: text/html

	<html>
		<head><title>Deck Checks - recommend checks</title><link rel='stylesheet' href='style.css' /></head>
		<body>
			<h1>Recommended Checks</h1>
"""
	form = cgi.FieldStorage()
	with DeckDB() as db:
		db.checkEvent(form["event"].value, output)
		roundnum = db.get_round(db.getEventId(form["event"].value))
		output.pageHeader(db, form['event'].value, roundnum, form)
	if not check_login(output, form['event'].value, form['password'].value if 'password' in form else '', 'recommend'):
		return
	print """
		<p>
			Note: recommendations are currently completely random
		</p>
	"""
	recommend_checks(form["event"].value, form)
	output.printLink(form, 'root', 'Return to menu')
	print """
		</body>
	</html>
"""

def main(args):
	with DeckDB() as db:
		db.checkEvent(args[0], output)
	recommend_checks(args[0], {})

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
