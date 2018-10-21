#!/usr/bin/env python
import csv, sys, cgitb, os, cgi
from deck_mysql import DeckDB
from printers import TextOutput, HTMLOutput
from login import check_login

output = None

def update_settings(tournament, name, url, rounds, password, pairings, team):
	try:
		with DeckDB() as db:
			id = db.getEventId(tournament)
			db.update('tournaments', {'tournamentid':id}, {'name':name, 'url':url, 'rounds':rounds, 'password':password, 'pairings':'1' if pairings else '0', 'team':'1' if team else '0'})
			output.printMessage('Tournament settings updated')

	except Exception as e:
		output.printMessage("Failed to update settings: %s" % (e))

def print_settings(tournament):
	output.printMessage('Current Settings')
	try:
		with DeckDB() as db:
			id = db.getEventId(tournament)
			(name, url, rounds, password, pairings, team) = db.getEventSettings(id)
			output.printMessage('Event name = %s' % name)
			output.printMessage('Event url = %s' % url)
			output.printMessage('Event max rounds = %s' % rounds)
			output.printMessage('Event password = %s' % password)
			output.printMessage('Event pairings = %s' % pairings)
			output.printMessage('Event team = %s' % team)
	except Exception as e:
		output.printMessage('Failed to get settings: %s' % e)


def docgi():
	print """Content-type: text/html

	<html>
		<head><title>Deck Checks - event settings</title><link rel='stylesheet' href='style.css' /></head>
		<body>
			<h1>Event Settings</h1>
"""
	form = cgi.FieldStorage()
	with DeckDB() as db:
		db.checkEvent(form["event"].value, output)
		currentround = db.get_round(db.getEventId(form['event'].value))
		output.pageHeader(db, form['event'].value, currentround, form)
	if not check_login(output, form['event'].value, form['password'].value if 'password' in form else '', 'settings'):
		return
	if 'name' in form:
	
		update_settings(form['event'].value, form['name'].value, form['url'].value if 'url' in form else '', form['rounds'].value if 'rounds' in form else '', form['newpassword'].value if 'newpassword' in form else '', form['pairings'].value if 'pairings' in form else '', form['team'].value if 'team' in form else '')
	else:
		with DeckDB() as db:
			id = db.getEventId(form['event'].value)
			(name, url, rounds, password, pairings, team) = db.getEventSettings(id)
		print """
<p>Update settings:</p>
<form method='post'>
<input type='hidden' name='password' value='%s'/>
Name: <input type='text' name='name' value='%s'/><br/>
URL: <input type='text' name='url' value='%s'/><br/>
Rounds: <input type='text' name='rounds' value='%s'/><br/>
Password: <input type='text' name='newpassword' value='%s'/><br/>
Pairings: <input type='checkbox' name='pairings' %s/><br/>
Team: <input type='checkbox' name='team' %s/><br/>
<input type='submit' />
</form>
""" % (form['password'].value if 'password' in form else '', name, url, rounds, password, 'checked="true"' if pairings else '', 'checked="true"' if team else '')
	output.printLink(form, 'root', 'Return to menu')
	print """
		</body>
	</html>
"""


def main(args):
	with DeckDB() as db:
		db.checkEvent(args[0], output)

	
	print_settings(args[0])

if __name__ == "__main__":

	if 'REQUEST_URI' in os.environ:
		cgitb.enable()
		output = HTMLOutput()
		docgi()
	else:
		if len(sys.argv) < 2:
			print "Usage: settings.py <event>"
			sys.exit(1)
		
		output = TextOutput()
		main(sys.argv[1:])
