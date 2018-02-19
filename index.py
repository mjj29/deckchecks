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
"""
output.printMessage("Available events:")
with DeckDB() as db:
	for row in db.get_events():
		print "<h2><a href='%s/root'>%s</a></h2>" % (row[0],row[0])
print """
</body>
</html>
"""
