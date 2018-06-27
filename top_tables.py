#!/usr/bin/env python
import csv, sys, cgitb, os, cgi
from deck_mysql import DeckDB
from printers import TextOutput, HTMLOutput
from login import check_login

output = None

def top_tables(tournament, form):

	try:
		with DeckDB() as db:
			id = db.getEventId(tournament)
			tables = db.get_top_tables(id)
			with output.table("Table", "Score", "Name", "Previous Checks", "Score", "Name", "Previous Checks") as table:
				for row in tables:
					try:
						score = row[0]
						tablenum = row[1]
						(player1, player2) = db.get_table(id, tablenum)
						(name1, score1, _, _) = player1
						(name2, score2, _, _) = player2
						prevChecks1 = db.getPreviousChecks(id, name1)
						prevChecks2 = db.getPreviousChecks(id, name2)
						table.printRow(
							output.makeLink(form, 'get_table?table=%s'%tablenum, tablenum),
							score1,
							output.makeLink(form, 'get_player?name=%s'%name1, name1),
							", ".join([str(x) for x in prevChecks1]),
							score2,
							output.makeLink(form, 'get_player?name=%s'%name2, name2),
							", ".join([str(x) for x in prevChecks2]))
					except:
						pass

	except Exception as e:
		output.printMessage("Failed to print top tables: %s" % (e))

def docgi():
	print """Content-type: text/html

	<html>
		<head><title>Deck Checks - top tables</title><link rel='stylesheet' href='style.css' /></head>
		<body>
			<h1>Top tables</h1>
""" 
	form = cgi.FieldStorage()
	with DeckDB() as db:
		db.checkEvent(form["event"].value, output)
		roundnum = db.get_round(db.getEventId(form["event"].value))
		output.pageHeader(db, form['event'].value, roundnum, form)
	if not check_login(output, form['event'].value, form['password'].value if 'password' in form else '', 'top_tables'):
		return
	top_tables(form["event"].value, form)
	output.printLink(form, 'export?type=top', 'Download as TSV')
	output.printLink(form, 'root', 'Return to menu')
	print """
		</body>
	</html>
"""

def main(args):
	with DeckDB() as db:
		db.checkEvent(args[0], output)
	top_tables(args[0], {})

if __name__ == "__main__":

	if 'REQUEST_URI' in os.environ:
		cgitb.enable()
		output = HTMLOutput()
		docgi()
	else:
		if len(sys.argv) < 2:
			print "Usage: top_tables.py <event>"
			sys.exit(1)
		
		output = TextOutput()
		main(sys.argv[1:])
