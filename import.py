#!/usr/bin/env python
from deck_mysql import DeckDB 
from printers import HTMLOutput, TextOutput
import csv, sys, os, cgi, cgitb, urllib2, bs4
from login import check_login

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


def insertPairing(db, eventid, roundnum, table, player):
	(name, country, score) = player
	try:
		idn = db.find('players', {"name":name, 'tournamentid':eventid})[0]
	except Exception as e:
		try:
			db.insert('players', (name, country, eventid))
			idn = db.find('players', {'name':name, 'tournamentid':eventid})[0]
			db.insert('seatings', (idn, 0, eventid))
		except Exception as e:
			output.printMessage("Failed to add player %s (%s)" % (str(player), e))

	try:
		db.insert('pairings', (idn, roundnum, score, table, eventid))
	except:
		pass

def parseSeatingRow(row):
	table = row[0]
	name = row[1].strip()
	country = ""
	score = 0

	return (table, (name, country, score), None)
	
def importAllDataURL(event, pairingsurl, clear):
	output.printMessage("Loading data from %s" % pairingsurl)
	sys.stdout.flush()
	rnd = 0
	with DeckDB() as db:
		id = db.getEventId(event)
		if clear:
			output.printMessage("Deleting previous data");
			db.deleteRow('pairings', {'tournamentid':id})
			db.deleteRow('seatings', {'tournamentid':id})
			db.deleteRow('players', {'tournamentid':id})

		while True:
			rnd = rnd + 1
			html = urllib2.urlopen(pairingsurl+'/'+str(rnd)).read()

			soup =  bs4.BeautifulSoup(html)

			table = soup.find('table')
			if not table: break
			output.printMessage("Importing data for round %s" % rnd)
			sys.stdout.flush()
			counter = 0
			for row in table.find_all('tr'):
				(table, name, points, opponent) = row.find_all('td')[0:4]
				try:
					table = int(table.get_text())
					player = (name.get_text(), '', int(points.get_text()))
					if rnd == 1:
						insertSeating(db, id, table, player)
					insertPairing(db, id, rnd, table, player)
				except Exception as e:
					try:
						output.printMessage("Failed to import row: %s: %s" % (row.get_text(), e))
					except:
						output.printMessage('Failed to import row: %s' % e)
				counter = counter + 1
			output.printMessage("Imported %d pairings" % counter)
			sys.stdout.flush()
		rnd = rnd - 1
		output.printMessage("Imported %d rounds" % rnd)
		try:
			db.deleteRow('round', {'tournamentid':id})
			db.insert('round', [rnd, id])
		except Exception as e:
			output.printMessage("Failed to update current round number: %s" % e)

def parseRow(row, wltr):
	# wltr = "Table","Player 1","Country","Points","Player 2","Country","Points"
	# pairings.cfb = Table	Player 1	Score	Player2
	if wltr:
		if "-" == row[0]:
			name1 = row[1].strip()
			country1 = row[2]
			score1 = int(row[3])
			return (0, (name1, country1, score1), None)
		else:
			table = int(row[0])
			name1 = row[1].strip()
			country1 = row[2]
			score1 = int(row[3])
			try:
				name2 = row[4].strip()
				country2 = row[5]
				score2 = int(row[6])

				return (table, (name1, country1, score1), (name2, country2, score2))
			except Exception as e:
				return (table, (name1, country1, score1), None)
	else:
		table = row[0]
		name1 = row[1].strip()
		country1 = ""
		score1 = row[2]
		try:
			name2 = row[3].strip()
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
			db.deleteRow('pairings', {'tournamentid':id})
			db.deleteRow('seatings', {'tournamentid':id})
			db.deleteRow('players', {'tournamentid':id})
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
			db.deleteRow('pairings', {'tournamentid':id, 'round':roundnum})
		for row in reader:
			if len(row) == 0: continue
			try:
				(table, player1, player2) = parseRow(row, wltr)
				count = count + 1
			except Exception as e:
				output.printMessage("Failed to import row %s: %s" % (row, e))
				continue

			try:
				insertPairing(db, id, roundnum, table, player1)
			except Exception as e:
				output.printMessage("Failed to import row %s: %s" % (row, e))
			if False:
				try:
					insertPairing(db, id, roundnum, table, player2)
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
		<head><title>Deck Checks - import data</title><link rel='stylesheet' href='style.css' /></head>
		<body>
			<h1>Import data</h1>
"""
	form = cgi.FieldStorage()
	with DeckDB() as db:
		db.checkEvent(form["event"].value, output)
		currentround = db.get_round(db.getEventId(form['event'].value))
		url = db.getEventUrl(db.getEventId(form['event'].value))
		output.pageHeader(db, form['event'].value, currentround, form)
	if not check_login(output, form['event'].value, form['password'].value if 'password' in form else '', 'import'):
		return
	if 'clear' in form:
		clear = True if form['clear'].value else False
	else:
		clear = False
	if "data" in form:
		if 'round' in form:
			roundnum = int(form['round'].value)
		else:
			roundnum = 0
		import_data(form["event"].value, form["type"].value, form["data"].value, clear, roundnum)
	elif 'pairingsurl' in form:
		importAllDataURL(form['event'].value, form['pairingsurl'].value, clear)
	else:
		print """
<div>
<form method='post'>
	<input type='hidden' name='password' value='%s'/>
	Clear data: <input type='checkbox' name='clear' value='true' /><br/>
	Import all data from CFB Event URL: <input type='text' name='pairingsurl' value='%s'/> <input type='submit'/>
</form>
</div>
<div>
<form method='post'>
	<input type='hidden' name='password' value='%s'/>
	Enter data:
	<select name='type'>
		<option value='pairings' selected='true'>Pairings</option>
		<option value='seatings'>Seatings</option>
	</select><br/>
	Clear data: <input type='checkbox' name='clear' value='true' /><br/>
	Import round: <input type='text' name='round' value='%s' /><br/>
	<textarea name='data' cols='80' rows='20'></textarea><br/>
	<input type='submit' />
</form>
</div>
<h2>Instructions</h2>
<p>
The simplest way to import data for a GP or other event on CFB pairings site is just to put the pairings URL into the top form. That will load all data up until this point, assuming R1 pairings are original decklist tables and all byes are sorted alphabetically. For more complex use cases, use the other forms. You can manually important seatings and then use the URL import to load the pairings.
</p>
<h3>Seatings</h3>
<p>
Seatings should be tab-separated, two columns:
</p>
<pre>Original table or player number &lt;tab&gt; Surname, First Names</pre>
<p>
(The name should match exactly the format that WLTR will produce for pairings).
</p>
<p>
You can get this by having 2 columns in Excel, selecting and copying them, then pasting into this dialog. Select 'Clear data' to replace existing seatings. Deselect if you want to add further seatings (such as byes) in addition to the current seatings. The 'Import round' field is ignored for seatings.
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
<p>NOTE: this will only work in <b>Firefox</b>, <b>Chrome</b> or <b>Safari</b>. It won't work in Internet Explorer or Edge.</p>
<p>NOTE: you will see warnings failing to import the header and footer of the page. This is entirely normal.</p>
<p>
Select 'Clear data' to replace existing pairings for a round. Leave unselected to import new pairings for a round.
</p>
<h3>Adding late players</h3>
<p>
If you do nothing and import pairings containing the new players they will be imported with a start table of 0. Alternatively, 
You can enter a line like:<br/>
&lt;number&gt;&lt;tab&gt;&lt;surname, name&gt;<br/>
Import seatings without clear and this will add an additional player with the given starting table number.
</p>
""" % (form['password'].value if 'password' in form else '', url,form['password'].value if 'password' in form else '',  currentround+1)

	output.printLink(form, 'root', 'Return to menu')
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
	elif args[1] == "url":
		importAllDataURL(args[0], args[2], True)
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
