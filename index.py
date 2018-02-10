#!/usr/bin/env python
from deck_mysql import DeckDB 
from printers import HTMLOutput, TextOutput
import csv, sys, os, cgi, cgitb

cgitb.enable()

print """Content-type: text/html

<html>
<head><title>Deck Checks</title></head>
<body>
<h1>Deck Checks</h1>
"""
with DeckDB() as db:
	for row in db.get_events():
		print "<h2><a href='%s/root'>%s</a></h2>" % (row[0],row[0])
print """
</body>
</html>
"""
