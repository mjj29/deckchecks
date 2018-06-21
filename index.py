#!/usr/bin/env python
from deck_mysql import DeckDB 
from printers import HTMLOutput, TextOutput
import csv, sys, os, cgi, cgitb

cgitb.enable()

output = HTMLOutput()

print """Content-type: text/html

<html>
<head><title>Deck Checks</title><link rel='stylesheet' href='style.css' /></head>
<body>
	<h1>Deck Checks</h1>
	<h2>Select an event</h2>
	<ul>
"""
with DeckDB() as db:
	for row in db.get_events():
		print "<li><b><a href='%s/root'>%s</a></b></li>" % (row[0],row[1])
print """
	</ul>
	<h2><a href='addevent'>Add new event</a></h2>
</body>
</html>
"""
