#!/usr/bin/env python
from deck_mysql import DeckDB 
from printers import HTMLOutput, TextOutput
import csv, sys, os, cgi, cgitb

output = None

def addevent(event):
	with DeckDB() as db:
		try:
			db.insert('tournaments', [event])
			id = db.getEventId(event)
			db.insert('round', [0, id])
		except Exception as e:
			output.printMessage("Failed to add event: %s" % e)

def main(args):
	addevent(args[0])

if __name__ == "__main__":
	
	if len(sys.argv) < 2:
		print "Usage: addevent <event>"
		sys.exit(1)
	
	output = TextOutput()
	main(sys.argv[1:])

