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
		'pairings':['playerid', 'score', 'tablenum', 'tournamentid'],
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


	def get_top_tables(self):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT score, tablenum FROM pairings GROUP BY tablenum ORDER BY score DESC, tablenum LIMIT 100")
			return cur.fetchall()

	def get_recommendations(self, tournamentid):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT name, score, tablenum, buildtable FROM players INNER JOIN seatings ON players.playerid=seatings.playerid INNER JOIN pairings ON players.playerid=pairings.playerid WHERE players.tournamentid=%s ORDER BY tablenum", (tournamentid))
			rows = cur.fetchall()
			tables = {}
			for r in rows:
				try:
					l = tables.get(r[2], list())
					l.append((r[0], r[1], r[2], r[3]))
					tables[r[2]] = l
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



	def get_table(self, tournamentid, tablenum):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT name, score, tablenum, buildtable FROM players INNER JOIN seatings ON players.playerid=seatings.playerid INNER JOIN pairings ON players.playerid=pairings.playerid WHERE tablenum=%s AND players.tournamentid=%s", (tablenum, tournamentid))
			rows = cur.fetchall()
			return ((rows[0][0], rows[0][1], rows[0][2], rows[0][3]), (rows[1][0], rows[1][1], rows[1][2], rows[1][3]))

	def get_table_ids(self, tournamentid, tablenum):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT players.playerid FROM players INNER JOIN seatings ON players.playerid=seatings.playerid INNER JOIN pairings ON players.playerid=pairings.playerid WHERE tablenum=%s AND players.tournamentid=%s", (tablenum, tournamentid))
			rows = cur.fetchall()
			return (rows[0][0], rows[1][0])


	def get_players(self, tournamentid, name):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT name, score, tablenum, buildtable FROM players INNER JOIN seatings ON players.playerid=seatings.playerid INNER JOIN pairings ON players.playerid=pairings.playerid WHERE name COLLATE LATIN1_GENERAL_CI  LIKE %s AND players.tournamentid=%s", ('%'+name+'%', tournamentid))
			rows = cur.fetchall()
			return [(row[0], row[1], row[2], row[3]) for row in rows]

	def getPreviousChecks(self, tournamentid, name):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT deckchecks.round FROM deckchecks INNER JOIN players on deckchecks.playerid=players.playerid WHERE deckchecks.tournamentid=%s AND players.name=%s", (tournamentid, name))
			rows = cur.fetchall()
			return [row[0] for row in rows]



