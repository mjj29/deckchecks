#!/usr/bin/env python
from deck_mysql import DeckDB 
import csv, sys

def insertSeating(table, idn, name):

	with DeckDB() as db:
		db.insert('players', (idn, name))
		db.insert('seatings', (idn, table))


def insertPairing(table, idn, score):

	with DeckDB() as db:
		db.insert('pairings', (idn, score, table))

def parseRow(row):
	table = int(row[0])
	id1 = int(row[1])
	name1 = row[2]
	id2 = int(row[3])
	name2 = row[4]
	score1 = int(row[5])
	score2 = int(row[6])

	return (table, (id1, name1, score1), (id2, name2, score2))

def import_seatings(seatingsFile):

	with open(seatingsFile) as f:
		reader = csv.reader(f)
		count = 0
		for row in reader:
			if len(row) == 0: continue
			try:
				(table, (id1, name1, score1), (id2, name2, score2)) = parseRow(row)
				count = count + 1
			except Exception as e:
				print "Failed to import row %s: %s" % (row, e)
				continue

			if 0 == table:
				insertSeating(table, id1, name1)
			else:
				insertSeating(table, id1, name1)
				insertSeating(table, id2, name2)
		print "Imported %d seatings" % count

def import_pairings(pairingsFile):

	with open(pairingsFile) as f:
		reader = csv.reader(f)
		count = 0
		for row in reader:
			if len(row) == 0: continue
			try:
				(table, (id1, name1, score1), (id2, name2, score2)) = parseRow(row)
				count = count + 1
			except Exception as e:
				print "Failed to import row %s: %s" % (row, e)
				continue

			if 0 == table:
				insertPairing(table, id1, score1)
			else:
				insertPairing(table, id1, score1)
				insertPairing(table, id2, score2)
		print "Imported %d pairings" % count



def main(args):
	if args[0] == "seatings":
		import_seatings(args[1])
	elif args[0] == "pairings":
		import_pairings(args[1])
	else:
		print "Unknown type "+args[0]

if __name__ == "__main__":
	
	if len(sys.argv) < 3:
		print "Usage: import [seatings|pairings] <file>"
		sys.exit(1)
	
	main(sys.argv[1:])
