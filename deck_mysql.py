import MySQLdb, sys, random
from mysql_passwords import database, user, password
from swisscalc import calculateTop8Threshold

class DeckCursor:
	def __init__(self, cur):
		self.cur = cur
	def __enter__(self):
		return self.cur
	def __exit__(self, type, value, traceback):
		self.cur.close()

class DeckDB:
	
	schema = {
		'pairings':['playerid', 'round', 'score', 'tablenum', 'tournamentid'],
		'seatings':['playerid', 'buildtable', 'tournamentid'],
		'players':['name', 'country', 'tournamentid'],
		'deckchecks':['playerid', 'teamplayer', 'tournamentid', 'round'],
		'round':['roundnum', 'tournamentid'],
		'tournaments':['name', 'url', 'rounds', 'password', 'pairings', 'team', 'decklisturl'],
	}

	def __init__(self):
		self.db = MySQLdb.connect(host='localhost', user=user, passwd=password, db=database)
		self.seatletters=['A','B','C']

	def __enter__(self):
		return self

	def __exit__(self, type, value, traceback):
		self.db.commit()
		self.db.close()

	def commit(self):
		self.db.commit()

	def cursor(self):
		return DeckCursor(self.db.cursor())

	def checkEvent(self, event, output):
		try:
			id = self.getEventId(event)
		except:
			output.printMessage("Unknown event %s" % event)
			sys.exit(0)
	
	def find(self, table, search):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT * FROM "+table+" WHERE "+(" AND ".join([x+'="'+str(search[x])+'"' for x in search.keys()])))
			return cur.fetchall()[0]
		
	def deleteRow(self, table, search):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("DELETE FROM "+table+" WHERE "+(" AND ".join([x+'="'+str(search[x])+'"' for x in search.keys()])))
		
	def clearTable(self, table):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("DELETE FROM %s" % table)
			self.db.commit()

	def update(self, table, matches, values):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("UPDATE "+table+" SET " +(', '.join([str(x)+'="'+str(values[x])+'"' for x in values])) + " WHERE " + (' AND '.join([str(x)+'="'+str(matches[x])+'"' for x in matches])))
			self.db.commit()

	def insert(self, table, data):

		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("INSERT INTO %s (%s) VALUES (%s)" % (table, ",".join(self.schema[table]), ",".join(["%s" for x in data])), data)
			self.db.commit()

	def get_round(self, tournamentid):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT * FROM round WHERE tournamentid=%s", tournamentid)
			rows = cur.fetchall()
			return int(rows[0][0])

	def getEventId(self, event):
		try:
			return int(event)
		except:
			with DeckCursor(self.db.cursor()) as cur:
				cur.execute("SELECT tournamentid FROM tournaments WHERE name=%s", event)
				rows = cur.fetchall()
				return int(rows[0][0])

	def isEventTeam(self, eventid):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT team FROM tournaments WHERE tournamentid=%s", eventid)
			rows = cur.fetchall()
			return True if rows[0][0] else False

	def hasEventPairings(self, eventid):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT pairings FROM tournaments WHERE tournamentid=%s", eventid)
			rows = cur.fetchall()
			return True if rows[0][0] else False

	def getEventSettings(self, eventid):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT name, url, rounds, password, pairings, team, decklisturl FROM tournaments WHERE tournamentid=%s", eventid)
			rows = cur.fetchall()
			return rows[0]

	def getEventPassword(self, eventid):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT password FROM tournaments WHERE tournamentid=%s", eventid)
			rows = cur.fetchall()
			return rows[0][0]


	def getEventName(self, eventid):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT name FROM tournaments WHERE tournamentid=%s", eventid)
			rows = cur.fetchall()
			return rows[0][0]


	def getEventRounds(self, eventid):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT rounds FROM tournaments WHERE tournamentid=%s", eventid)
			rows = cur.fetchall()
			return int(rows[0][0])


	def getDecklistUrl(self, eventid):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT decklisturl FROM tournaments WHERE tournamentid=%s", eventid)
			rows = cur.fetchall()
			return rows[0][0]


	def getEventUrl(self, eventid):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT url FROM tournaments WHERE tournamentid=%s", eventid)
			rows = cur.fetchall()
			return rows[0][0]

	def getPlayersForEachByeNumber(self, eventid):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("""
SELECT round-1 AS byes, count(round) AS players FROM (
	SELECT min(round) AS round FROM
		pairings INNER JOIN 
		players ON
			pairings.playerid=players.playerid
	WHERE players.tournamentid=%s GROUP BY name)
	AS minRounds
GROUP BY round
ORDER BY byes
""", eventid)
			rows = cur.fetchall()
			result = []
			b = 0
			for (byes, number) in rows:
				while b < byes:
					b = b + 1
					result.append(0)
				result.append(number)
				b = b + 1
		return result


	def get_events(self):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT tournamentid, name, url FROM tournaments")
			return cur.fetchall()

	def get_all_checks(self, event):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT round, name, teamplayer FROM deckchecks INNER JOIN players ON deckchecks.playerid=players.playerid WHERE deckchecks.tournamentid=%s ORDER BY round DESC", event)
			rows = cur.fetchall()
			currentround = 0
			checks = {}
			for row in rows:
				if row[0] != currentround:
					currentround = row[0]
					checks[currentround] = []
				checks[currentround].append((row[1], row[2]))
		return checks


	def get_pairings(self, tournamentid, roundnum=None):
		roundnum = roundnum or self.get_round(tournamentid)
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("""
SELECT lpair.tablenum, lname, lscore, rname, rscore FROM (
	SELECT name AS lname, players.playerid AS lid, score AS lscore, tablenum
		FROM players INNER JOIN pairings
		ON players.playerid=pairings.playerid
		WHERE pairings.tournamentid=%s AND pairings.round=%s
) AS lpair INNER JOIN (
	SELECT name AS rname, players.playerid AS rid, score AS rscore, tablenum 
		FROM players INNER JOIN pairings ON players.playerid=pairings.playerid
		WHERE pairings.tournamentid=%s AND pairings.round=%s
) AS rpair
ON lpair.tablenum=rpair.tablenum AND lid!=rid and lpair.tablenum != 0
ORDER BY lname
""", (tournamentid, roundnum, tournamentid, roundnum))
			return cur.fetchall()


	def get_top_tables(self, tournamentid, roundnum=None):
		roundnum = roundnum or self.get_round(tournamentid)
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT MAX(score), tablenum FROM pairings WHERE tournamentid=%s AND round=%s GROUP BY tablenum ORDER BY MAX(score) DESC, tablenum LIMIT 100", (tournamentid, roundnum))
			return cur.fetchall()

	def get_recommendations(self, tournamentid, roundnum=None, n=6, rand=True):
		roundnum = roundnum or self.get_round(tournamentid)
		if rand:
			marginalthreshold=0
			additionalFilters=""
		else:
			playersWithEachByes = self.getPlayersForEachByeNumber(tournamentid)
			totalRounds = self.getEventRounds(tournamentid)
			(marginalthreshold, top8threshold, undefeatedthreshold) =calculateTop8Threshold(playersWithEachByes, totalRounds, roundnum)
			additionalFilters="AND deckchecks.playerid is NULL"

		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("""
SELECT players.playerid, name, score, buildtable 
FROM players INNER JOIN seatings 
	ON players.playerid=seatings.playerid 
INNER JOIN pairings 
	ON players.playerid=pairings.playerid 
LEFT OUTER JOIN deckchecks 
	ON deckchecks.playerid=players.playerid
WHERE players.tournamentid=%s
	AND pairings.round=%s 
	AND pairings.score>=%s
"""+additionalFilters+" ORDER BY tablenum", (tournamentid, roundnum, marginalthreshold))
			rows = cur.fetchall()
			tables = {}
			for r in rows:
				try:
					prevtables = self.get_prev_tables(tournamentid, r[0])
					l = tables.get(prevtables[-1], list())
					l.append((r[1], r[2], prevtables, r[3]))
					tables[prevtables[-1]] = l
				except:
					pass

			rv = []
			for i in range(0, n):
				k = random.choice(tables.keys())
				try:
					rv.append((k, tables[k][0], tables[k][1]))
				except:
					pass

			return rv


	def get_build_table(self, tournamentid, tablenum):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT players.playerid, name, MAX(score), buildtable FROM players INNER JOIN seatings ON players.playerid=seatings.playerid INNER JOIN pairings ON players.playerid=pairings.playerid WHERE buildtable=%s AND players.tournamentid=%s GROUP BY name, buildtable", (tablenum, tournamentid))
			rows = cur.fetchall()
			return [(r[1], r[2], self.get_prev_tables(tournamentid, r[0]), r[3]) for r in rows]


	def hasSeating(self, tournamentid):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT * FROM players INNER JOIN seatings on players.playerid=seatings.playerid WHERE players.tournamentid=%s", (tournamentid))
			rows = cur.fetchall()
			return True if len(rows) > 0 else False
	
	def get_table(self, tournamentid, tablenum, roundnum=None):
		roundnum = roundnum or self.get_round(tournamentid)
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT players.playerid, name, score, buildtable FROM players INNER JOIN seatings ON players.playerid=seatings.playerid INNER JOIN pairings ON players.playerid=pairings.playerid WHERE tablenum=%s AND players.tournamentid=%s AND pairings.round=%s", (tablenum, tournamentid, roundnum))
			rows = cur.fetchall()
			return ((rows[0][1], rows[0][2], self.get_prev_tables(tournamentid, rows[0][0]), rows[0][3]), (rows[1][1], rows[1][2], self.get_prev_tables(tournamentid, rows[1][0]), rows[1][3]))

	def get_table_ids(self, tournamentid, tablenum, roundnum=None):
		roundnum = roundnum or self.get_round(tournamentid)
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT players.playerid FROM players INNER JOIN seatings ON players.playerid=seatings.playerid INNER JOIN pairings ON players.playerid=pairings.playerid WHERE tablenum=%s AND players.tournamentid=%s AND round=%s", (tablenum, tournamentid, roundnum))
			rows = cur.fetchall()
			return (rows[0][0], rows[1][0])

	def get_player_id(self, tournamentid, name):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT playerid FROM players WHERE players.tournamentid=%s AND name COLLATE LATIN1_GENERAL_CI = %s", (tournamentid, name))
			rows = cur.fetchall()
			return rows[0][0]

	def get_prev_tables(self, tournamentid, playerid):
		currentround = self.get_round(tournamentid)
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT round, tablenum FROM pairings WHERE tournamentid=%s AND playerid=%s ORDER BY round", (tournamentid, playerid))
			rows = cur.fetchall()
			rv = []
			c = 0
			for r in rows:
				rnd = r[0]
				tbl = r[1]
				for i in range(c, rnd-1):
					rv.append('Bye')
				c = rnd
				rv.append(tbl)
			for i in range(c, currentround):
				rv.append('-')
		return rv

	def getAllPlayers(self, tournamentid):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT name, buildtable FROM players INNER JOIN seatings on players.playerid=seatings.playerid WHERE players.tournamentid=%s"%tournamentid)
			rows = cur.fetchall()
		return [(row[0], row[1]) for row in rows]

	def get_players(self, tournamentid, name):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT players.playerid, name, MAX(score), buildtable FROM players INNER JOIN seatings ON players.playerid=seatings.playerid LEFT OUTER JOIN pairings ON players.playerid=pairings.playerid WHERE name COLLATE LATIN1_GENERAL_CI  LIKE %s AND players.tournamentid=%s GROUP BY name", ('%'+name+'%', tournamentid))
			rows = cur.fetchall()
		return [(row[1], row[2], self.get_prev_tables(tournamentid, row[0]), row[3]) for row in rows]

	def getPreviousChecks(self, tournamentid, name):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT deckchecks.round, deckchecks.teamplayer FROM deckchecks INNER JOIN players on deckchecks.playerid=players.playerid WHERE deckchecks.tournamentid=%s AND players.name=%s", (tournamentid, name))
			rows = cur.fetchall()
			if self.isEventTeam(tournamentid):
				return ["%s:%s" % (row[0],self.seatletters[row[1]]) for row in rows]
			else:
				return [row[0] for row in rows]



