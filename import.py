#!/usr/bin/env python
from deck_mysql import DeckDB 
from printers import HTMLOutput, TextOutput
import csv, sys, os, cgi, cgitb

output = None

def insertSeating(db, eventid, table, player):

	(name, country, score) = player
	try:
		db.insert('players', (name, country, eventid))
	except:
		pass
	idn = db.find('players', {"name":name, 'tournamentid':eventid})[0]
	try:
		db.insert('seatings', (idn, table, eventid))
	except:
		pass


def insertPairing(db, eventid, table, player):
	(name, country, score) = player
	try:
		idn = db.find('players', {"name":name, 'tournamentid':eventid})[0]

		try:
			db.insert('pairings', (idn, score, table, eventid))
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

def import_seatings_reader(event, reader, clear):
	count = 0
	with DeckDB() as db:
		id = db.getEventId(event)
		if clear:
			output.printMessage("Deleting previous data");
			db.deleteRow('players', {'tournamentid':id})
			db.deleteRow('seatings', {'tournamentid':id})
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
				insertSeating(db, id, table, player1)
			except Exception as e:
				output.printMessage("Failed to import row %s: %s" % (row, e))
			if player2:
				try:
					insertSeating(db, id, table, player2)
				except Exception as e:
					output.printMessage("Failed to import row %s: %s" % (row, e))
	output.printMessage("Imported %d seatings" % count)

def import_pairings_reader(event, reader, clear, roundnum, wltr):
	count = 0
	with DeckDB() as db:
		try:
			id = db.getEventId(event)
			db.deleteRow('round', {'tournamentid':id})
			db.insert('round', [roundnum, id])
		except Exception as e:
			output.printMessage("Failed to update current round number: %s" % e)
		if clear:
			output.printMessage("Deleting previous data");
			db.deleteRow('pairings', {'tournamentid':id})
		for row in reader:
			if len(row) == 0: continue
			try:
				(table, player1, player2) = parseRow(row, wltr)
				count = count + 1
			except Exception as e:
				output.printMessage("Failed to import row %s: %s" % (row, e))
				continue

			try:
				insertPairing(db, id, table, player1)
			except Exception as e:
				output.printMessage("Failed to import row %s: %s" % (row, e))
			if player2:
				try:
					insertPairing(db, id, table, player2)
				except Exception as e:
					output.printMessage("Failed to import row %s: %s" % (row, e))
	output.printMessage("Imported %d pairings" % count)

def import_seatings_file(event, seatingsFile, clear):

	with open(seatingsFile) as f:
		reader = csv.reader(f, delimiter='\t')
		import_seatings_reader(event, reader, clear)


def import_pairings_file(event, pairingsFile, clear, roundnum):

	with open(pairingsFile) as f:
		data = f.read()
	import_pairings_data(event, data, clear, roundnum)

def import_seatings_data(event, seatData, clear):
	reader = csv.reader(seatData.split('\n'), delimiter='\t')
	import_seatings_reader(event, reader, clear)


def import_pairings_data(event, pairingData, clear, roundnum):
	if '\t' in pairingData:
		reader = csv.reader(pairingData.split('\n'), delimiter='\t')
		wltr=False
	else:
		reader = csv.reader(pairingData.split('\n'))
		wltr=True
	import_pairings_reader(event, reader, clear, roundnum, wltr)

def import_data(event, dtype, data, clear, roundnum):
	if "seatings" == dtype:
		import_seatings_data(event, data, clear)
	elif "pairings" == dtype:
		import_pairings_data(event, data, clear, roundnum)
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
	with DeckDB() as db:
		db.checkEvent(form["event"].value, output)
	output.printMessage("Tournament is %s" % form["event"].value)
	if "data" in form:
		if 'clear' in form:
			clear = True if form['clear'].value else False
		else:
			clear = False
		if 'round' in form:
			roundnum = int(form['round'].value)
		else:
			roundnum = 0
		import_data(form["event"].value, form["type"].value, form["data"].value, clear, roundnum)
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
<h2>Instructions</h2>
<h3>Seatings</h3>
<p>
Seatings should be tab-separated, two columns:
</p>
<pre>Original table or player number &lt;tab&gt; Surname, First Names</pre>
<p>
(The name should match exactly the format that WLTR will produce for pairings).
</p>
<p>
You can get this by having 2 columns in Excel, selecting and copying them, then pasting into this dialog. Select 'Clear data' to replace existing seatings. Deselect if you want to add further seatings (such as byes) in addition to the current seatings. The 'Current round' field is ignored for seatings.
</p>
<h3>Pairings</h3>
<p>
Pairings can either be copied from WLTR, in which case the format should be:
</p>
<pre>"Table","Surname, Forename","Country","Points","Surname, Forename","Country","Points"</pre>
<p>
Alternatively, they can be copied from <a href="http://pairings.channelfireball.com/pairings">http://pairings.channelfireball.com/pairings</a>. In that case, just use select-all, copy then past into this dialog. That will be in the format:
</p>
<pre>Table &lt;tab&gt; Surname, Firstname &lt;tab&gt; Score &lt;tab&gt; Surname, Firstname </pre>
<p>
Select 'Clear data' to replace existing pairings. The pairings aren't stored per-round so you will normally select 'Clear data' when importing pairings for the next round. The 'Current round' field is purely information and will be displayed on the pages to look up names and tables so that people know which round's data is in the app.
</p>
"""

	print """
		</body>
	</html>
"""



def main(args):
	with DeckDB() as db:
		db.checkEvent(args[0], output)
	if args[1] == "seatings":
		import_seatings_file(args[0], args[2], True)
	elif args[1] == "pairings":
		import_pairings_file(args[0], args[2], True, 0)
	else:
		print "Unknown type "+args[1]

if __name__ == "__main__":
	
	if 'REQUEST_URI' in os.environ:
		cgitb.enable()
		output = HTMLOutput()
		docgi()
	else:
		if len(sys.argv) < 4:
			print "Usage: import <event> [seatings|pairings] <file>"
			sys.exit(1)
		
		output = TextOutput()
		main(sys.argv[1:])
