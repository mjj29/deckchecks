#!/usr/bin/env python
from deck_mysql import DeckDB 
import sys

def main(args):
	with DeckDB() as db:
		with db.cursor() as cur:
			try:
				cur.execute("DROP TABLE `players`")
			except:
				pass
		with db.cursor() as cur:
			try:
				cur.execute("DROP TABLE `round`")
			except:
				pass
		with db.cursor() as cur:
			try:
				cur.execute("DROP TABLE `seatings`")
			except:
				pass
		with db.cursor() as cur:
			try:
				cur.execute("DROP TABLE `pairings`")
			except:
				pass
	with DeckDB() as db:
		with db.cursor() as cur:
			cur.execute("CREATE TABLE `round` (roundnum INT)")
			cur.execute("INSERT INTO `round` (roundnum) values (0)")
		with db.cursor() as cur:
			cur.execute("CREATE TABLE `players` (playerid INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(100), country VARCHAR(100), UNIQUE KEY player_key (name, country))")
		with db.cursor() as cur:
			cur.execute("CREATE TABLE `seatings` (playerid INT UNIQUE, buildtable INT, INDEX ididx(playerid), CONSTRAINT fkidseat FOREIGN KEY (playerid) REFERENCES players(playerid) ON DELETE CASCADE ON UPDATE CASCADE)")
		with db.cursor() as cur:
			cur.execute("CREATE TABLE `pairings` (playerid INT UNIQUE, score INT, tablenum INT, INDEX ididx(playerid), CONSTRAINT fkidpair FOREIGN KEY (playerid) REFERENCES players(playerid) ON DELETE CASCADE ON UPDATE CASCADE)")
		db.commit()

if __name__ == "__main__":
	
	main(sys.argv[1:])
