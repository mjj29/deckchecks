#!/usr/bin/env python
from deck_mysql import DeckDB 
import sys

print "You didn't want this, it drops the whole database"
return

def main(args):
	tables = [ 
		('tournaments', ['CREATE table `tournaments` (tournamentid INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(100) UNIQUE, url VARCHAR(100), password VARCHAR(100), rounds INT)']),
		("players", ["CREATE TABLE `players` (playerid INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(100), country VARCHAR(100), tournamentid INT, CONSTRAINT fkidtourp FOREIGN KEY (tournamentid) REFERENCES tournaments(tournamentid) ON DELETE CASCADE ON UPDATE CASCADE, UNIQUE KEY player_key (tournamentid, name, country))"]),
		('round', ["CREATE TABLE `round` (roundnum INT, tournamentid INT, CONSTRAINT fkidtourr FOREIGN KEY (tournamentid) REFERENCES tournaments(tournamentid) ON DELETE CASCADE ON UPDATE CASCADE)"]),
		('seatings', ["CREATE TABLE `seatings` (playerid INT UNIQUE, buildtable INT, tournamentid INT, INDEX ididx(playerid), CONSTRAINT fkidseat FOREIGN KEY (playerid) REFERENCES players(playerid) ON DELETE CASCADE ON UPDATE CASCADE, CONSTRAINT fkidtours FOREIGN KEY (tournamentid) REFERENCES tournaments(tournamentid) ON DELETE CASCADE ON UPDATE CASCADE)"]),
		('pairings', ["CREATE TABLE `pairings` (playerid INT, round INT, score INT, tablenum INT, tournamentid INT, UNIQUE KEY pairings_key (tournamentid, playerid, round), INDEX ididx(playerid), CONSTRAINT fkidpair FOREIGN KEY (playerid) REFERENCES players(playerid) ON DELETE CASCADE ON UPDATE CASCADE, CONSTRAINT fkidtoura FOREIGN KEY (tournamentid) REFERENCES tournaments(tournamentid) ON DELETE CASCADE ON UPDATE CASCADE)"]),
		('deckchecks', ["CREATE TABLE `deckchecks` (playerid INT, tournamentid INT, round INT, UNIQUE KEY checks_key (playerid, tournamentid, round), INDEX ididx(playerid), CONSTRAINT fkiddeck FOREIGN KEY (playerid) REFERENCES players(playerid) ON DELETE CASCADE ON UPDATE CASCADE, CONSTRAINT fkidtourd FOREIGN KEY (tournamentid) REFERENCES tournaments(tournamentid) ON DELETE CASCADE ON UPDATE CASCADE)"]),
	]
	with DeckDB() as db:
		for (t, _) in reversed(tables):
			with db.cursor() as cur:
				try:
					print "DROP TABLE `%s`" % t
					cur.execute("DROP TABLE `%s`" % t)
				except:
					pass
		db.commit()
	with DeckDB() as db:
		for (_, queries) in tables:
				for q in queries:
					with db.cursor() as cur:
						try:
							print q
							cur.execute(q)
						except:
							pass
		db.commit()

if __name__ == "__main__":
	
	main(sys.argv[1:])
