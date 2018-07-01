#!/usr/bin/env python
import csv, sys, cgitb, os, cgi
from deck_mysql import DeckDB
from printers import TextOutput, HTMLOutput
from login import check_login
import deckcheck

output = None

def allchecks(tournament, form):

	try:
		with DeckDB() as db:
			id = db.getEventId(tournament)
			maxrounds = db.get_round(id)

			headers = output.getHeaders(maxrounds)

			checks = db.get_all_checks(id)
			for rn in reversed(sorted(checks.keys())):
				output.heading("Round %s"%rn)
				with output.table(*headers) as table:
					for name in checks[rn]:
						players = db.get_players(id, name)
						for p in players:
								output.printPlayer(p, db, id, form)

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
		output.pageHeader(db, form['event'].value, roundnum, form)
	if not check_login(output, form['event'].value, form['password'].value if 'password' in form else '', 'allchecks'):
		return
	if "tables" in form and form['tables']:
		deckcheck.output = output
		for table in form['tables'].value.split():
			deckcheck.mark_checked(form["event"].value, table=table, roundnum=form['round'].value)
	else:
		print """
			<h2>Check tables</h2>
			<p>Enter one table per line</p>
			<form>
			<input type='hidden' name='password' value='%s'/>
			<textarea name='tables' cols='30' rows='5'></textarea>
			<br/>
			<input type='text' name='round' value='%s'/>
			<br/>
			<input type='submit' value='Mark as checked' />
			</form>
""" % (form['password'].value if 'password' in form else '', roundnum)
		allchecks(form["event"].value, form)
	output.printLink(form, 'export?type=checks', 'Download as TSV')
	output.printLink(form, 'root', 'Return to menu')
	print """
		</body>
	</html>
"""

def main(args):
	with DeckDB() as db:
		db.checkEvent(args[0], output)
	allchecks(args[0], {})

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
