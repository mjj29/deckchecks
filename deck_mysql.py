import MySQLdb, sys, random

class DeckCursor:
	def __init__(self, cur):
		self.cur = cur
	def __enter__(self):
		return self.cur
	def __exit__(self, type, value, traceback):
		self.cur.close()

class DeckDB:
	
	database = 'deckchecks'
	user = 'deckchecks'
	password = 'Sans1orbia'
	schema = {
		'pairings':['playerid', 'round', 'score', 'tablenum', 'tournamentid'],
		'seatings':['playerid', 'buildtable', 'tournamentid'],
		'players':['name', 'country', 'tournamentid'],
		'deckchecks':['playerid', 'tournamentid', 'round'],
		'round':['roundnum', 'tournamentid'],
		'tournaments':['name'],
	}

	def __init__(self):
		self.db = MySQLdb.connect(host='localhost', user=self.user, passwd=self.password, db=self.database)

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
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT tournamentid FROM tournaments WHERE name=%s", event)
			rows = cur.fetchall()
			return int(rows[0][0])

	def get_events(self):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT name FROM tournaments")
			return cur.fetchall()

	def get_all_checks(self, event):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT round, name FROM deckchecks INNER JOIN players ON deckchecks.playerid=players.playerid WHERE deckchecks.tournamentid=%s ORDER BY round", event)
			rows = cur.fetchall()
			currentround = 0
			checks = {}
			for row in rows:
				if row[0] != currentround:
					currentround = row[0]
					checks[currentround] = []
				checks[currentround].append(row[1])
		return checks


	def get_top_tables(self, tournamentid, roundnum=None):
		roundnum = roundnum or self.get_round(tournamentid)
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT MAX(score), tablenum FROM pairings WHERE tournamentid=%s AND round=%s GROUP BY tablenum ORDER BY MAX(score) DESC, tablenum LIMIT 100", (tournamentid, roundnum))
			return cur.fetchall()

	def get_recommendations(self, tournamentid, roundnum=None):
		roundnum = roundnum or self.get_round(tournamentid)
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT players.playerid, name, score, buildtable FROM players INNER JOIN seatings ON players.playerid=seatings.playerid INNER JOIN pairings ON players.playerid=pairings.playerid WHERE players.tournamentid=%s AND pairings.round=%s ORDER BY tablenum", (tournamentid, roundnum))
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
			for i in range(0, 6):
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

	def get_players(self, tournamentid, name):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT players.playerid, name, MAX(score), buildtable FROM players INNER JOIN seatings ON players.playerid=seatings.playerid LEFT OUTER JOIN pairings ON players.playerid=pairings.playerid WHERE name COLLATE LATIN1_GENERAL_CI  LIKE %s AND players.tournamentid=%s GROUP BY name", ('%'+name+'%', tournamentid))
			rows = cur.fetchall()
		return [(row[1], row[2], self.get_prev_tables(tournamentid, row[0]), row[3]) for row in rows]

	def getPreviousChecks(self, tournamentid, name):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT deckchecks.round FROM deckchecks INNER JOIN players on deckchecks.playerid=players.playerid WHERE deckchecks.tournamentid=%s AND players.name=%s", (tournamentid, name))
			rows = cur.fetchall()
			return [row[0] for row in rows]



