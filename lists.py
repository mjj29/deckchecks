#!/usr/bin/env python
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

import csv, sys, cgitb, os, cgi
from deck_mysql import DeckDB
from printers import TextOutput, HTMLOutput
from login import check_login
from cfb import CFBTournament

output = None

def lists(tournament):

	try:
		with DeckDB() as db:
			id = db.getEventId(tournament)
			
			decklisturl=db.getDecklistUrl(id)
			if 'json' in decklisturl:
				t = CFBTournament({'id':id, 'name':'Event', 'pairingsurl':db.getEventUrl(id), 'decklist_list_url':decklisturl})
				online = t.getPlayersWithDecklists()
			else:
				online = set()
			records = db.getAllPlayers(id)
			tables = {}
			for (name, buildtable) in records:
				tables[name] = buildtable
			players = set([name for (name, buildtable) in records])
			paperLists = players-online

			paperTables = {}
			for player in paperLists:
				paperTables[player]=tables[player]
				

			with output.table("Name", "Build table") as table:
				for player, tbl in sorted(paperTables.iteritems(), key=lambda (k,v): (v,k)):
					try:
						table.printRow(player, tbl)
					except Exception as e:
						print "<p>%s</p>" % str(e)

	except Exception as e:
		output.printMessage("Failed to print lists: %s" % (e))

def docgi():
	print """Content-type: text/html

	<html>
		<head><title>Lists</title><link rel='stylesheet' href='style.css' /></head>
		<body>
""" 
	form = cgi.FieldStorage()
	with DeckDB() as db:
		db.checkEvent(form["event"].value, output)
		print "<h1>Lists excluding online</h1>"
		roundnum = db.get_round(db.getEventId(form["event"].value))
		output.pageHeader(db, form['event'].value, roundnum, form)
		print "<p>List of players who didn't submit online decklists, sorted by build table / starting table. Note, if this is not a CFB event with online decklists then this will just be the master list of all players by table numbers, with byes first on table '0', alphabetically.</p>"

	if not check_login(output, form['event'].value, form['password'].value if 'password' in form else '', 'lists'):
		return
	lists(form["event"].value)
	output.printLink(form, 'root', 'Return to menu')
	print """
		</body>
	</html>
"""

def main(args):
	with DeckDB() as db:
		db.checkEvent(args[0], output)
	lists(args[0])

if __name__ == "__main__":

	if 'REQUEST_URI' in os.environ:
		cgitb.enable()
		output = HTMLOutput()
		docgi()
	else:
		if len(sys.argv) < 2:
			print "Usage: lists.py <event>"
			sys.exit(1)
		
		output = TextOutput()
		main(sys.argv[1:])
