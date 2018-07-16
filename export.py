#!/usr/bin/env python
import csv, sys, cgitb, os, cgi
from deck_mysql import DeckDB
from printers import TSVOutput, TextOutput
import top_tables, allchecks, pairings

def docgi():
	print """Content-type: text/csv

""" 
	form = cgi.FieldStorage()
	with DeckDB() as db:
		db.checkEvent(form["event"].value, TextOutput())
	if 'type' in form and form['type']:
		if "top" == form['type'].value:
			top_tables.output = TSVOutput()
			top_tables.top_tables(form["event"].value, {})
		elif "checks" == form['type'].value:
			allchecks.output = TSVOutput()
			allchecks.allchecks(form["event"].value, {})
		elif "pairings" == form['type'].value:
			pairings.output = TSVOutput()
			pairings.pairings(form["event"].value)
		else:
			print "ERROR: type must be top, pairings or checks"
	else:
		print "ERROR: must specify type"

def main(args):
	with DeckDB() as db:
		db.checkEvent(args[1], TextOutput())
	if "top" == args[0]:
		top_tables.output = TSVOutput()
		top_tables.top_tables(args[1])
	elif "checks" == args[0]:
		allchecks.output = TSVOutput()
		allchecks.allchecks(args[1])
	else:
		print "Type must be top or checks";

if __name__ == "__main__":

	if 'REQUEST_URI' in os.environ:
		cgitb.enable()
		docgi()
	else:
		if len(sys.argv) < 3:
			print "Usage: export.py <type> <event>"
			sys.exit(1)
		
		main(sys.argv[1:])
