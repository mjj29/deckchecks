#!/usr/bin/env python
from deck_mysql import DeckDB 
from printers import HTMLOutput, TextOutput
import csv, sys, os, cgi, cgitb, subprocess
from mysql_passwords import database, user, password

output = None

def createbackup(filename):
	with DeckDB() as db:
		args=['mysqldump', '-u', user, '--password='+password, database]
		with open(filename, 'w') as f:
			subprocess.check_call(args, stdout=f)

def restorebackup(filename):
	with DeckDB() as db:
		args=['mysql', '-u', user, '--password='+password, '-D', database]
		with open(filename) as f:
			subprocess.check_call(args, stdin=f)

def main(args):
	if args[0] == "create":
		createbackup(args[1])
	elif args[0] == "restore":
		restorebackup(args[1])
	else:
		print "Usage: backup [create|restore] <file>"
		sys.exit(1)

if __name__ == "__main__":
	
	if len(sys.argv) < 3:
		print "Usage: backup [create|restore] <file>"
		sys.exit(1)
	
	output = TextOutput()
	main(sys.argv[1:])

