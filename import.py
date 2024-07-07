#!/usr/bin/env python
from deck_mysql import DeckDB 
from printers import HTMLOutput, TextOutput
import csv, sys, os, cgi, cgitb, urllib2, bs4, subprocess, re, json
from login import check_login
import xml.etree.ElementTree as ET
from cfb import CFBTournament

output = None

def insertSeating(db, eventid, table, player):

	(name, country, score, decklistid) = player
	name = re.sub(r'[^\x00-\x7f]',r'', name) 
	try:
		idn = db.find('players', {"name":name, 'tournamentid':eventid})[0]
	except:
		db.insert('players', (name, country, eventid, decklistid))
		idn = db.find('players', {"name":name, 'tournamentid':eventid})[0]
	try:
		db.insert('seatings', (idn, table, eventid))
	except:
		try:
			db.update('seatings', {'playerid':idn, 'tournamentid':eventid}, {'buildtable':table})
		except Exception as e:
			output.printMessage('Failed to add or update seating for %s (%s)' % (name, e))


def insertPairing(db, eventid, roundnum, table, player):
	(name, country, score, decklistid) = player
	name = re.sub(r'[^\x00-\x7f]',r'', name) 
	try:
		idn = db.find('players', {"name":name, 'tournamentid':eventid})[0]
	except Exception as e:
		try:
			db.insert('players', (name, country, eventid, decklistid))
			idn = db.find('players', {'name':name, 'tournamentid':eventid})[0]
			if int(roundnum) == 1:
				output.printMessage("Adding player to seatings at table %s" % table)
				db.insert('seatings', (idn, table, eventid))
			else:
				output.printMessage("Adding player as bye in round %s" % roundnum)
				db.insert('seatings', (idn, 0, eventid))
		except Exception as e:
			output.printMessage("Failed to add player %s (%s)" % (str(player), e))

	try:
		db.insert('pairings', (idn, roundnum, score, table, eventid))
	except:
		pass

def parseSeatingRow(row, mode):
	if mode=='MELEE':
		table = row[9]
		name = row[20]
		country = ""
		score = 0
		decklistid = ""
	else:
		table = row[0]
		name = row[1].strip()
		country = ""
		score = 0
		decklistid=''

	return (table, (name, country, score, decklistid), None)
	
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

		if 'json' in pairingsurl:
			t = CFBTournament({'id':id,'name':event,'pairings_url':pairingsurl,'decklist_list_url':db.getDecklistUrl(id)})
			rnd = t.getRound()
			count = 0
			for (_, table, player) in t.getPairings():
				if rnd == 1 and not db.hasSeating(id):
					insertSeating(db, id, table, player)
				insertPairing(db, id, rnd, table, player)
				count = count + 1
			output.printMessage('Imported %d players in round %d' % (count, rnd))
			try:
				db.deleteRow('round', {'tournamentid':id})
				db.insert('round', [rnd, id])
			except Exception as e:
				output.printMessage("Failed to update current round number: %s" % e)
		elif 'channelfireball' in pairingsurl:
			while True:
				rnd = rnd + 1
				html = urllib2.urlopen(pairingsurl+'/'+str(rnd)).read()

				soup =  bs4.BeautifulSoup(html)

				table = soup.find('table')
				if not table: break
				try:
					output.printMessage("Importing data for round %s" % rnd)
					sys.stdout.flush()
					counter = 0
					for row in table.find_all('tr'):
						(table, name, points, opponent) = row.find_all('td')[0:4]
						try:
							table = int(table.get_text())
							player = (name.get_text(), '', int(points.get_text()))
							if rnd == 1 and not db.hasSeating(id):
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
				except:
					output.printMessage("Failed to import round, assuming that was all of them")
					break
			rnd = rnd - 1
			output.printMessage("Imported %d rounds" % rnd)
			try:
				db.deleteRow('round', {'tournamentid':id})
				db.insert('round', [rnd, id])
			except Exception as e:
				output.printMessage("Failed to update current round number: %s" % e)
		elif 'mtgpairings' in pairingsurl:
			
			html = urllib2.urlopen(pairingsurl).read()
			soup =  bs4.BeautifulSoup(html)

			for td in soup.find_all('td', onclick=re.compile('.*/Round/View')):
				if 'Round' in td.string:
					rnd = int(re.sub('Round', '', td.string).strip())
					url = 'http://mtgpairings.com'+re.sub(".*'(.*)'", r'\1', td['onclick'])
					try:
						html2 = urllib2.urlopen(url).read()
						soup2 = bs4.BeautifulSoup(html2)
						counter = 0
						for tr in soup2.find_all('tr'):
							tds = tr.find_all('td')
							try:
								table=int(tds[0].string.strip())
								player = (tds[1].string.strip(), '', int(tds[2].string.strip()))
								if rnd == 1 and not db.hasSeating(id):
									insertSeating(db, id, table, player)
								insertPairing(db, id, rnd, table, player)
								counter = counter + 1
							except:
								output.printMessage('Failed to import row %s' % str(tds))
						output.printMessage('Imported %d pairings' % counter)
					except:
						output.printMessage('Failed to read round data for round %s from %s' % (rnd, url))
			output.printMessage('Imported %d rounds' % rnd)
			try:
				db.deleteRow('round', {'tournamentid':id})
				db.insert('round', [rnd, id])
			except Exception as e:
				output.printMessage("Failed to update current round number: %s" % e)
		elif 'cfbevents' in pairingsurl:
			
			html = urllib2.urlopen(pairingsurl).read()
			soup =  bs4.BeautifulSoup(html)

			rndhtml = soup.find('h1', class_='display-4')
			if not rndhtml: raise Exception("Could not find round number")
			rnd=int(re.sub('^[^0-9]*([0-9]*)[^0-9].*$', r'\1', rndhtml.get_text().replace('\n', '')))
			output.printMessage("Importing round %s"%rnd)
			
			table = soup.find('table')
			if not table: raise Exception("Could not find pairings table")
			try:
				counter = 0
				for row in table.find_all('tr'):
					try:
						row = row.find_all('td')+["0"]
						(table, name, points) = row[0:3]
						table = int(table.get_text())
						try:
							player = (name.get_text(), '', int(points.get_text()))
						except:
							player = (name.get_text(), '', 0)
						if rnd == 1 and not db.hasSeating(id):
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
			except Exception as e:
				output.printMessage('Failed to import pairings: %s' %e)
			try:
				db.deleteRow('round', {'tournamentid':id})
				db.insert('round', [rnd, id])
			except Exception as e:
				output.printMessage("Failed to update current round number: %s" % e)
		else:
			raise Exception("Unknown pairings site: %s" % pairingsurl)

def parseRow(row, mode):
	# wltr = "Table","Player 1","Country","Points","Player 2","Country","Points"
	# wltr teams = "Table","Player 1","Points","Player 2","Points"
	# pairings.cfb = Table	Player 1	Score	Player2
	if mode=='WLTR':
		if "-" == row[0]:
			name1 = row[1].strip()
			country1 = row[2]
			try:
				score1 = int(row[3])
			except:
				score1 = 0
			return (0, (name1, country1, score1, ''), None)
		else:
			table = int(row[0])
			name1 = row[1].strip()
			country1 = row[2]
			try:
				score1 = int(row[3])
			except:
				score1 = 0
			try:
				name2 = row[4].strip()
				country2 = row[5]
				try:
					score2 = int(row[6])
				except:
					score2 = 0

				return (table, (name1, country1, score1, ''), (name2, country2, score2, ''))
			except Exception as e:
				return (table, (name1, country1, score1, ''), None)
	elif mode=='MELEE':
		table = row[43]
		name1 = row[14]
		deckid1 = row[64]
		country1 = ""
		score1 = 0
		try: score1 = int(row[27]) # Competitors1GameWins?
		except: pass
		output.printMessage("player1="+str((name1, country1, score1, deckid1)))
		try:
			name2 = row[44]
			country2 = ""
			score2 = 0
			try: score2 = int(row[95]) # Competitors2GameWins?
			except: pass
			deckid2 = row[98]
			output.printMessage("player2="+str((name2, country2, score2, deckid2)))
			return (table, (name1, country1, score1, deckid1), (name2, country2, score2, deckid2))
		except Exception as e:
			return (table, (name1, country1, score1, deckid1), None)
	else:
		table = row[0]
		name1 = row[1].strip()
		country1 = ""
		score1 = row[2]
		try:
			name2 = row[3].strip()
			country2 = ""
			score2 = row[2]
			return (table, (name1, country1, score1, ''), (name2, country2, score2, ''))
		except Exception as e:
			return (table, (name1, country1, score1, ''), None)

def import_melee_json_seatings(event, clear, seatData):
	output.printMessage("Importing Melee-format JSON")
	seats = json.loads(seatData)
	count = 0
	with DeckDB() as db:
		id = db.getEventId(event)
		if clear:
			output.printMessage("Deleting previous data");
			db.deleteRow('pairings', {'tournamentid':id})
			db.deleteRow('seatings', {'tournamentid':id})
			db.deleteRow('players', {'tournamentid':id})
		for s in seats:
			table = s['TableNumber']
			name = s['Name']
			count = count + 1
			output.printMessage("Adding Table "+str(table)+": "+name)
			insertSeating(db, id, table, (name, '', 0, ''))
	output.printMessage("Imported %d seatings" % count)



def import_seatings_reader(event, reader, clear, mode):
	count = 0
	with DeckDB() as db:
		id = db.getEventId(event)
		if clear:
			output.printMessage("Deleting previous data");
			db.deleteRow('pairings', {'tournamentid':id})
			db.deleteRow('seatings', {'tournamentid':id})
			db.deleteRow('players', {'tournamentid':id})
		for row in reader:
			print str(row)
			output.printMessage("%s"%row)
			if len(row) == 0 or 'DateCreated' in row[0]: continue
			try:
				(table, player1, player2) = parseSeatingRow(row, mode)
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

def import_pairings_reader(event, reader, clear, roundnum, mode):
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
			if len(row) == 0 or 'Competitors1TeamPlayers1TeamId' in row[0]: continue
			try:
				(table, player1, player2) = parseRow(row, mode)
				count = count + 1
			except Exception as e:
				output.printMessage("Failed to import row %s: %s" % (row, e))
				raise
				continue

			try:
				insertPairing(db, id, roundnum, table, player1)
			except Exception as e:
				output.printMessage("Failed to import row %s: %s" % (row, e))
				raise
			if mode=='MELEE' and player2:
				try:
					insertPairing(db, id, roundnum, table, player2)
				except Exception as e:
					output.printMessage("Failed to import row %s: %s" % (row, e))
					raise
	output.printMessage("Imported %d pairings" % count)

def import_melee_json_pairings(event, roundnum, clear, matchData, standingsData):
	output.printMessage("Importing Melee-format JSON")
	matches = json.loads(matchData)
	points = {}
	if standingsData:
		for s in json.loads(standingsData):
			points[s['Team']['Players'][0]['ID']]=s['Points']
	else:
		output.printMessage("WARNING: No standings data so cannot import current scores for top-cut calculations. If this is not round 1, re-run with standings at the end of the previous round added as well")
	count = 0
	with DeckDB() as db:
		id = db.getEventId(event)
		try:
			db.deleteRow('round', {'tournamentid':id})
			db.insert('round', [roundnum, id])
		except Exception as e:
			output.printMessage("Failed to update current round number: %s" % e)
		if clear:
			output.printMessage("Deleting previous data");
			db.deleteRow('pairings', {'tournamentid':id, 'round':roundnum})
		for m in matches:
			table = m['TableNumber']
			name1 = m['Competitors'][0]['Team']['Players'][0]['Name']
			score1 = points.get(m['Competitors'][0]['Team']['Players'][0]['ID'], 0)
			decklistid1 = ''
			if len(m['Competitors'][0]['Decklists'])>0:
				decklistid1 = m['Competitors'][0]['Decklists'][0]['DecklistId']
			player1=(name1,'',score1,decklistid1)
			insertPairing(db, id, roundnum, table, player1)
			name2="Bye"
			if len(m['Competitors'])>1:
				name2 = m['Competitors'][1]['Team']['Players'][0]['Name']
				score2 = points.get(m['Competitors'][1]['Team']['Players'][0]['ID'], 0)
				decklistid2 = ''
				if len(m['Competitors'][1]['Decklists'])>0:
					decklistid2 = m['Competitors'][1]['Decklists'][0]['DecklistId']
				player2=(name2,'',score2,decklistid2)
				insertPairing(db, id, roundnum, table, player2)
			count = count + 1
			output.printMessage("Adding Table "+str(table)+": "+name1+" vs "+name2)
	output.printMessage("Imported %d pairings" % count)



def import_seatings_file(event, seatingsFile, clear):

	with open(seatingsFile) as f:
		reader = csv.reader(f, delimiter='\t')
		import_seatings_reader(event, reader, clear)

def import_all_xml(event, data, clear):
	with DeckDB() as db:
		id = db.getEventId(event)
		if clear:
			output.printMessage("Deleting previous data");
			db.deleteRow('pairings', {'tournamentid':id})
			db.deleteRow('seatings', {'tournamentid':id})
			db.deleteRow('players', {'tournamentid':id})

		root = ET.fromstring(data)
		participants = {}
		for team in root.findall('participation')[0].findall('team'):
			name = team.get('name')
			pid = team.get('id')
			participants[pid] = (name, '', 0)
		for person in root.findall('participation')[0].findall('person'):
			name = person.get('last')+', '+person.get('first')
			pid = person.get('id')
			participants[pid] = (name, person.get('country'), 0)

		roundnum = 0
		for rnd in root.findall('matches')[0].findall('round'):
			roundnum = rnd.get('number')
			output.printMessage('Importing data for round %s' % roundnum)
			table = 0
			for match in rnd.findall('match'):
				try:
					table = table + 1
					player1 = participants[match.get('person')]
					player2 = participants[match.get('opponent')]
					if int(roundnum) == 1:
						insertSeating(db, id, table, player1)
						insertSeating(db, id, table, player2)
					insertPairing(db, id, roundnum, table, player1)
					insertPairing(db, id, roundnum, table, player2)
				except Exception as e:
					output.printMessage('Failed to import match: %s' % e)
		output.printMessage("Imported %s rounds" % roundnum)
		try:
			db.deleteRow('round', {'tournamentid':id})
			db.insert('round', [roundnum, id])
		except Exception as e:
			output.printMessage("Failed to update current round number: %s" % e)

def import_round_pdf(event, data, clear, roundnum, seatings=False):

	with open('/tmp/import.pdf', 'wb') as f:
		f.write(data)
	subprocess.check_call(['/usr/bin/pdftotext', '/tmp/import.pdf'])

	with DeckDB() as db:
		try:
			id = db.getEventId(event)
			db.deleteRow('round', {'tournamentid':id})
			db.insert('round', [roundnum, id])
		except Exception as e:
			output.printMessage("Failed to update current round number: %s" % e)
		if clear:
			output.printMessage("Deleting previous data");
			if seatings:
				db.deleteRow('pairings', {'tournamentid':id})
				db.deleteRow('seatings', {'tournamentid':id})
				db.deleteRow('players', {'tournamentid':id})
			else:
				db.deleteRow('pairings', {'tournamentid':id, 'round':roundnum})

		start = False
		mode='table'
		with open('/tmp/import.txt') as f:
			for l in f:
				if l.startswith('----'):
					start = True
					l = l.replace('-', '')
				l = l.strip()
				if start:
					if mode=='table':
						table=int(l)
						mode='name1'
					elif mode=='name1':
						name1=l
						mode='dci1'
					elif mode=='dci1':
						mode='name2'
					elif mode=='name2':
						name2=l
						mode='dci2'
					elif mode=='dci2':
						mode='score'
					elif mode=='score':
						scores = l.split('-')
						score1 = int(scores[0])
						score2 = int(scores[1])
						mode='table'
						player1 = (name1, '', score1)
						player2 = (name2, '', score2)
						
						if int(roundnum) == 1:
							insertSeating(db, id, table, player1)
							insertSeating(db, id, table, player2)
						insertPairing(db, id, roundnum, table, player1)
						insertPairing(db, id, roundnum, table, player2)
					
		output.printMessage("Imported %s rounds" % roundnum)
		try:
			db.deleteRow('round', {'tournamentid':id})
			db.insert('round', [roundnum, id])
		except Exception as e:
			output.printMessage("Failed to update current round number: %s" % e)

def import_pairings_file(event, pairingsFile, clear, roundnum):

	with open(pairingsFile) as f:
		data = f.read()
	import_pairings_data(event, data, clear, roundnum)

def import_seatings_data(event, seatData, clear, meleejson):
	if meleejson:
		import_melee_json_seatings(event, clear, seatData)
		return
	mode='STANDARD'
	if seatData.startswith('%PDF'):
		output.printMessage("Importing as PDF")
		import_round_pdf(event, seatData, clear, 0, seatings=True)
		return
	elif '\t' in seatData:
		output.printMessage("Importing as tab-separated")
		reader = csv.reader(seatData.split('\n'), delimiter='\t')
	else:
		output.printMessage("Importing as comma-separated")
		reader = csv.reader(seatData.split('\n'))
	if 'DisplayNameLastFirst' in seatData: mode='MELEE'
	import_seatings_reader(event, reader, clear, mode)


def import_pairings_data(event, pairingData, clear, roundnum, standings, meleejson):
	if meleejson:
		import_melee_json_pairings(event, roundnum, clear, pairingData, standings)
		return
	mode='STANDARD'
	if pairingData.startswith('<'):
		output.printMessage("Importing as XML")
		import_all_xml(event, pairingData, clear)
		return
	elif pairingData.startswith('%PDF'):
		output.printMessage("Importing as PDF")
		import_round_pdf(event, pairingData, clear, roundnum, seatings=False)
		return
	elif '\t' in pairingData:
		output.printMessage("Importing as tab-separated")
		reader = csv.reader(pairingData.split('\n'), delimiter='\t')
	else:
		output.printMessage("Importing as comma-separated")
		reader = csv.reader(pairingData.split('\n'))
	if 'Country' in pairingData.split('\n')[0]: mode='WLTR'
	if 'Competitors1TeamPlayers1TeamId' in pairingData: mode='MELEE'
	import_pairings_reader(event, reader, clear, roundnum, mode)

def import_data(event, dtype, data, clear, roundnum, standings=None, meleejson=False):
	if 'Wizards Event Reporter' in data:
		d = []
		for l in data.split('\n'):
			l = re.sub(r'([0-9]*) ([^0-9]*) *[0-9]* *([^0-9]*) *[0-9]* ([0-9]*)-([0-9]*)', r'\1\t\2\t\4\t\3\t\5', l)
			d.append(l)
		data = '\n'.join(d)
	if "seatings" == dtype:
		import_seatings_data(event, data, clear, meleejson)
	elif "pairings" == dtype:
		import_pairings_data(event, data, clear, roundnum, standings, meleejson)
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
	if 'round' in form:
		roundnum = int(form['round'].value)
	else:
		roundnum = 0
	if 'datafile' in form and form['datafile'].value:
		import_data(form["event"].value, form["type"].value, form['datafile'].file.read(), clear, roundnum)
	elif 'meleeseatings' in form and form['meleeseatings'].value and form['type'].value=='seatings':
		import_data(form["event"].value, form["type"].value, form['meleeseatings'].file.read(), clear, roundnum, meleejson=True)
	elif 'meleematches' in form and form['meleematches'].value and form['type'].value=='pairings':
		import_data(form["event"].value, form["type"].value, form['meleematches'].file.read(), clear, roundnum, standings=form['meleestandings'].file.read() if 'meleestandings' in form and form['meleestandings'].value else None, meleejson=True)
	elif 'pairingsurl' in form and form['pairingsurl'].value:
		importAllDataURL(form['event'].value, form['pairingsurl'].value, clear)
	elif "data" in form:
		import_data(form["event"].value, form["type"].value, form["data"].value, clear, roundnum)
	else:
		print """
<div>
<form method='post' enctype="multipart/form-data">
	<input type='hidden' name='password' value='%s'/>
	Clear data: <input type='checkbox' name='clear' value='true' /> [resets all tournament data including checks]<br/>
	Import all data from Pairings URL: <input type='text' name='pairingsurl' value='%s'/> <input type='submit'/>
</form>
</div>
<div>
<form method='post' enctype="multipart/form-data">
	<input type='hidden' name='password' value='%s'/>
	Enter data:
	<select name='type'>
		<option value='pairings' selected='true'>Pairings</option>
		<option value='seatings'>Seatings</option>
	</select><br/>
	Clear data: <input type='checkbox' name='clear' value='true' />[if importing seating resets all tournament data including checks]<br/>
	Import round: <input type='text' name='round' value='%s' /><br/>
	Import Melee JSON: <br/>
	<ul>
	<li><b>Seatings:</b> <input type='file' name='meleeseatings' /></li>
	<li><b>Matches:</b> <input type='file' name='meleematches' /></li>
	<li><b>Standings:</b><input type='file' name='meleestandings' /></li>
	</ul>
	Import from file: <input type='file' name='datafile' /><br/>
	<input type='submit' />
	<textarea name='data' cols='80' rows='20'></textarea><br/>
</form>
</div>
<h2>Instructions</h2>
<h3>Melee</h3>
<p>
For a Melee tournament you need to do the following, with downloads from the Melee Tournament Control page.
</p>
<h4>Constructed</h4>
<p>Go to Settings and put http://melee.gg/Decklist/View as the Decklist URL.</p>
<p>After pairing Round 1, download the JSON for the match data for Round 1, and uploaded it to the "Matches" option</p>
<p>After pairing subsequent rounds, download the JSON for that round's match data and the Standings for the previous round. Upload them to the "Matches" and "Standings" options respectively</p>
<h4>Sealed</h4>
<p>For seatings, download the JSON for the seatings data and upload it to the "Seatings" option, with the data type set to seatings</p>
<p>After pairing Round 1, download the JSON for the match data for Round 1, and uploaded it to the "Matches" option</p>
<p>After pairing subsequent rounds, download the JSON for that round's match data and the Standings for the previous round. Upload them to the "Matches" and "Standings" options respectively</p>
<h3>Old instructions</h3>
<p>
The simplest way to import data for a GP or other event on CFB pairings site is just to put the pairings URL into the top form. That will load all data up until this point, assuming R1 pairings are original decklist tables and all byes are sorted alphabetically. For more complex use cases, use the other forms. You can manually important seatings and then use the URL import to load the pairings, as long as you do not use clear.
</p>
<p>
There is also support for using mtgpairings.com to import from a URL. Put the event page URL into the URL dialog. This is the simplest way to import data for WER-based events.
</p>
<p>
For WER-based events, print pairings-by-name to file as a PDF, open the PDF, select the whole page (ctrl-A), copy and paste them in. Round one pairings will be used as seatings.
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
