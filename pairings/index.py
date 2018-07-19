#!/usr/bin/env python
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from deck_mysql import DeckDB 
from printers import HTMLOutput, TextOutput
import csv, sys, os, cgi, cgitb

cgitb.enable()

output = HTMLOutput()

print """Content-type: text/html

<html>
<head><title>Pairings</title><link rel='stylesheet' href='style.css' /></head>
<body>
	<h1>Pairings</h1>
	<h2>Select an event</h2>
	<ul>
"""
with DeckDB() as db:
	for row in db.get_events():
		if db.hasEventPairings(row[0]):
			print "<li><b><a href='%s/pairings'>%s</a></b></li>" % (row[0],row[1])
print """
	</ul>
</body>
</html>
"""
