#!/usr/bin/env python
from deck_mysql import DeckDB 
from printers import HTMLOutput, TextOutput
import csv, sys, os, cgi, cgitb

cgitb.enable()
output = HTMLOutput()

print """Content-type: text/html

<html>
<head><title>Deck Checks</title></head>
<body>
<h1>Deck Checks</h1>
"""
form = cgi.FieldStorage()
with DeckDB() as db:
	db.checkEvent(form["event"].value, output)
output.printMessage("Tournament is %s" % form["event"].value)
print """
<h2><a href='get_table'>Lookup by table</a></h2>
<h2><a href='get_player'>Lookup by player</a></h2>
<h2><a href='top_tables'>Check top tables</a></h2>
<h2><a href='recommend'>Recommend checks</a></h2>
<h2><a href='allchecks'>See all checks</a></h2>
<h2><a href='import'>Import data</a></h2>
</body>
</html>
"""
