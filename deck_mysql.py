import MySQLdb

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
		'pairings':['playerid', 'score', 'tablenum'],
		'seatings':['playerid', 'buildtable'],
		'players':['playerid', 'name'],
	}

	def __init__(self):
		self.db = MySQLdb.connect(host='localhost', user=self.user, passwd=self.password, db=self.database)

	def __enter__(self):
		return self

	def __exit__(self, type, value, traceback):
		self.db.close()

	def commit(self):
		self.db.commit()

	def cursor(self):
		return DeckCursor(self.db.cursor())
		
	def insert(self, table, data):

		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("INSERT INTO %s (%s) VALUES (%s)" % (table, ",".join(self.schema[table]), ",".join(["%s" for x in data])), data)
			self.db.commit()

	def get_table(self, tablenum):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT name, score, buildtable FROM players INNER JOIN seatings ON players.playerid=seatings.playerid INNER JOIN pairings ON players.playerid=pairings.playerid WHERE tablenum=%s", tablenum)
			rows = cur.fetchall()
			return ((rows[0][0], rows[0][1], rows[0][2]), (rows[1][0], rows[1][1], rows[1][2]))

	def get_players(self, name):
		with DeckCursor(self.db.cursor()) as cur:
			cur.execute("SELECT name, score, buildtable FROM players INNER JOIN seatings ON players.playerid=seatings.playerid INNER JOIN pairings ON players.playerid=pairings.playerid WHERE name COLLATE LATIN1_GENERAL_CI  LIKE %s", '%'+name+'%')
			rows = cur.fetchall()
			return [(row[0], row[1], row[2]) for row in rows]




