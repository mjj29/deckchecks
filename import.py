#!/usr/bin/env python
from deck_mysql import DeckDB 
from printers import HTMLOutput, TextOutput
import csv, sys, os, cgi, cgitb

output = None

def insertSeating(db, table, player):

	(name, country, score) = player
	try:
		db.insert('players', (name, country))
	except:
		pass
	idn = db.find('players', {"name":name})[0]
	try:
		db.insert('seatings', (idn, table))
	except:
		pass


def insertPairing(db, table, player):
	(name, country, score) = player
	try:
		idn = db.find('players', {"name":name})[0]

		try:
			db.insert('pairings', (idn, score, table))
		except:
			pass
	except:
		output.printMessage("Failed to lookup player %s" % str(player))

def parseSeatingRow(row):
	table = row[0]
	name = row[1]
	country = ""
	score = 0

	return (table, (name, country, score), None)
	

def parseRow(row, wltr):
	# wltr = "Table","Player 1","Country","Points","Player 2","Country","Points"
	# pairings.cfb = Table	Player 1	Score	Player2
	if wltr:
		if "-" == row[0]:
			name1 = row[1]
			country1 = row[2]
			score1 = int(row[3])
			return (0, (name1, country1, score1), None)
		else:
			table = int(row[0])
			name1 = row[1]
			country1 = row[2]
			score1 = int(row[3])
			try:
				name2 = row[4]
				country2 = row[5]
				score2 = int(row[6])

				return (table, (name1, country1, score1), (name2, country2, score2))
			except Exception as e:
				return (table, (name1, country1, score1), None)
	else:
		table = row[0]
		name1 = row[1]
		country1 = ""
		score1 = row[2]
		try:
			name2 = row[3]
			country2 = ""
			score2 = row[2]
			return (table, (name1, country1, score1), (name2, country2, score2))
		except Exception as e:
			return (table, (name1, country1, score1), None)

def import_seatings_reader(reader, clear):
	count = 0
	with DeckDB() as db:
		if clear:
			output.printMessage("Deleting previous data");
			db.clearTable('players')
			db.clearTable('seatings')
		for row in reader:
			output.printMessage("%s"%row)
			if len(row) == 0: continue
			try:
				(table, player1, player2) = parseSeatingRow(row)
				count = count + 1
			except Exception as e:
				output.printMessage("Failed to import row %s: %s" % (row, e))
				continue

			try:
				insertSeating(db, table, player1)
			except Exception as e:
				output.printMessage("Failed to import row %s: %s" % (row, e))
			if player2:
				try:
					insertSeating(db, table, player2)
				except Exception as e:
					output.printMessage("Failed to import row %s: %s" % (row, e))
	output.printMessage("Imported %d seatings" % count)

def import_pairings_reader(reader, clear, roundnum, wltr):
	count = 0
	with DeckDB() as db:
		try:
			db.clearTable('round')
			db.insert('round', [roundnum])
		except Exception as e:
			output.printMessage("Failed to update current round number: %s" % e)
		if clear:
			output.printMessage("Deleting previous data");
			db.clearTable('pairings')
		for row in reader:
			if len(row) == 0: continue
			try:
				(table, player1, player2) = parseRow(row, wltr)
				count = count + 1
			except Exception as e:
				output.printMessage("Failed to import row %s: %s" % (row, e))
				continue

			try:
				insertPairing(db, table, player1)
			except Exception as e:
				output.printMessage("Failed to import row %s: %s" % (row, e))
			if player2:
				try:
					insertPairing(db, table, player2)
				except Exception as e:
					output.printMessage("Failed to import row %s: %s" % (row, e))
	output.printMessage("Imported %d pairings" % count)

def import_seatings_file(seatingsFile, clear):

	with open(seatingsFile) as f:
		reader = csv.reader(f, delimiter='\t')
		import_seatings_reader(reader, clear)


def import_pairings_file(pairingsFile, clear, roundnum):

	with open(pairingsFile) as f:
		data = f.read()
	import_pairings_data(data, clear, roundnum)

def import_seatings_data(seatData, clear):
	reader = csv.reader(seatData.split('\n'), delimiter='\t')
	import_seatings_reader(reader, clear)


def import_pairings_data(pairingData, clear, roundnum):
	if '\t' in pairingData:
		reader = csv.reader(pairingData.split('\n'), delimiter='\t')
		wltr=False
	else:
		reader = csv.reader(pairingData.split('\n'))
		wltr=True
	import_pairings_reader(reader, clear, roundnum, wltr)

def import_data(dtype, data, clear, roundnum):
	if "seatings" == dtype:
		import_seatings_data(data, clear)
	elif "pairings" == dtype:
		import_pairings_data(data, clear, roundnum)
	else:
		output.printMessage("Unknown data type %s" % dtype)

def docgi():
	print """Content-type: text/html

	<html>
		<head><title>Deck Checks</title></head>
		<body>
			<h1>Deck Checks</h1>
"""
	form = cgi.FieldStorage()
	if "data" in form:
		if 'clear' in form:
			clear = True if form['clear'].value else False
		else:
			clear = False
		if 'round' in form:
			roundnum = int(form['round'].value)
		else:
			roundnum = 0
		import_data(form["type"].value, form["data"].value, clear, roundnum)
	else:
		print """
<form method='post'>
	Enter data:
	<select name='type'>
		<option value='pairings' selected='true'>Pairings</option>
		<option value='seatings'>Seatings</option>
	</select><br/>
	Clear data: <input type='checkbox' name='clear' value='true' checked='true' /><br/>
	Current round: <input type='text' name='round' value='0' /><br/>
	<textarea name='data' cols='80' rows='20'></textarea><br/>
	<input type='submit' />
</form>
"""

	print """
		</body>
	</html>
"""



def main(args):
	if args[0] == "seatings":
		import_seatings_file(args[1], True)
	elif args[0] == "pairings":
		import_pairings_file(args[1], True, 0)
	else:
		print "Unknown type "+args[0]

if __name__ == "__main__":
	
	if 'REQUEST_URI' in os.environ:
		cgitb.enable()
		output = HTMLOutput()
		docgi()
	else:
		if len(sys.argv) < 3:
			print "Usage: import [seatings|pairings] <file>"
			sys.exit(1)
		
		output = TextOutput()
		main(sys.argv[1:])
