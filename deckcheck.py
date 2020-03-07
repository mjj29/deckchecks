#!/usr/bin/env python
import csv, sys, cgitb, os, cgi
from deck_mysql import DeckDB
from printers import TextOutput, HTMLOutput
from login import check_login

output = None

def mark_checked(tournament, table=None, player=None, roundnum=None, seat=0, remove=False):

	if table:
		try:
			with DeckDB() as db:
				id = db.getEventId(tournament)
				if None == roundnum:
					roundnum = db.get_round(id)
				(player1, player2) = db.get_table_ids(id, table, roundnum=roundnum)
				if remove:
					db.deleteRow('deckchecks', {'playerid':player1, 'teamplayer':seat, 'tournamentid':id, 'round':roundnum})
					db.deleteRow('deckchecks', {'playerid':player2, 'teamplayer':seat, 'tournamentid':id, 'round':roundnum})
				else:
					db.insert('deckchecks', [player1, seat, id, roundnum])
					db.insert('deckchecks', [player2, seat, id, roundnum])

			if remove:
				output.printMessage("Marked table %s as not checked in round %s" % (table, roundnum))
			else:
				output.printMessage("Marked table %s as checked in round %s" % (table, roundnum))
		except Exception as e:
			output.printMessage("Failed to lookup table %s: %s" % (table, e))
	elif player:
		try:
			with DeckDB() as db:
				id = db.getEventId(tournament)
				playerid = db.get_player_id(id, player)
				round = db.get_round(id)
				if remove:
					db.deleteRow('deckchecks', {'playerid':playerid, 'teamplayer':seat, 'tournamentid':id, 'round':roundnum})
				else:
					db.insert('deckchecks', [playerid, seat, id, round])
			output.printMessage("Marked player %s as checked in round %s" % (player, round))
		except Exception as e:
			output.printMessage("Failed to lookup player %s: %s" % (player, e))


def docgi():
	print """Content-type: text/html

	<html>
		<head><title>Deck Checks - mark as checked</title><link rel='stylesheet' href='style.css' /></head>
		<body>
			<h1>Deck Checks</h1>
"""
	form = cgi.FieldStorage()
	with DeckDB() as db:
		db.checkEvent(form["event"].value, output)
		roundnum = db.get_round(db.getEventId(form["event"].value))
		output.pageHeader(db, form['event'].value, roundnum, form)
	if not check_login(output, form['event'].value, form['password'].value if 'password' in form else '', 'deckcheck'):
		return
	if "table" in form and form['table']:
		mark_checked(form["event"].value, table=int(form["table"].value), seat=int(form["seat"].value) if 'seat' in form else 0, remove=form["remove"] if 'remove' in form else False, roundnum=form['round'].value if 'round' in form else None)
		print """<script language="JavaScript" type="text/javascript"><!--
		setTimeout("window.history.go(-1)",3000);
		//--></script>"""

	elif 'player' in form and form['player']:
		mark_checked(form["event"].value, player=form["player"].value, seat=int(form["seat"].value) if 'seat' in form else 0, remove=form["remove"] if 'remove' in form else False, roundnum=form['round'].value if 'round' in form else None)
		print """<script language="JavaScript" type="text/javascript"><!--
		setTimeout("window.history.go(-2)",5000);
		//--></script>"""
	else:
		print """
<form>
			<input type='hidden' name='password' value='%s'/>
	Enter table number: <input type='text' name='table' /><input type='submit' /><br/>
	Enter player name: <input type='text' name='player' /><input type='submit' />
</form>
"""%(form['password'].value if 'password' in form else '')

	output.printLink(form, 'root', 'Return to menu')
	print """
		</body>
	</html>
"""

def main(args):
	with DeckDB() as db:
		db.checkEvent(args[0], output)
	table=None
	player=None
	try:
		table=int(args[1])
	except:
		player=args[1]
	mark_checked(args[0], player=player, table=table)

if __name__ == "__main__":

	if 'REQUEST_URI' in os.environ:
		cgitb.enable()
		output = HTMLOutput()
		docgi()
	else:
		if len(sys.argv) < 3:
			print "Usage: deckcheck.py <event> [<table number>|<player>]"
			sys.exit(1)
		
		output = TextOutput()
		main(sys.argv[1:])
