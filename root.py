#!/usr/bin/env python
from deck_mysql import DeckDB 
from printers import HTMLOutput, TextOutput
import csv, sys, os, cgi, cgitb
from login import check_login

cgitb.enable()
output = HTMLOutput()

print """Content-type: text/html

<html>
<head><title>Deck Checks - root</title><link rel='stylesheet' href='style.css' /></head>
<body>
<h1>Deck Checks</h1>
"""
form = cgi.FieldStorage()
with DeckDB() as db:
	db.checkEvent(form["event"].value, output)
	roundnum = db.get_round(db.getEventId(form["event"].value))
	output.pageHeader(db, form['event'].value, roundnum, form)
if check_login(output, form['event'].value, form['password'].value if 'password' in form else '', 'root'):
	output.printLink(form, 'get_table', 'Lookup by table')
	output.printLink(form, 'get_player', 'Lookup by player')
	output.printLink(form, 'top_tables', 'Check top tables')
	output.printLink(form, 'recommend', 'Recommend checks')
	output.printLink(form, 'lists', 'Show offline lists')
	output.printLink(form, 'allchecks', 'See all checks')
	output.printLink(form, 'pairings', 'Pairings')
	output.printLink(form, 'import', 'Import data')
	output.printLink(form, 'settings', 'Event settings')
print """
</body>
</html>
"""
