#!/usr/bin/env python
from deck_mysql import DeckDB 
from printers import HTMLOutput, TextOutput
from cfb import getCFBShows
import csv, sys, os, cgi, cgitb, urllib2, bs4, re

output = None

def addevent(event, url):
	with DeckDB() as db:
		try:
			db.insert('tournaments', [event, url, 15, '', False, False])
			id = db.getEventId(event)
			db.insert('round', [0, id])
		except Exception as e:
			output.printMessage("Failed to add event: %s" % e)

def docgi():
			
	print """Content-type: text/html

	<html>
		<head><title>Deck Checks - add event</title><link rel='stylesheet' href='style.css' /></head>
		<body>
			<h1>Add event</h1>
			<h2>Add event from CFB pairings</h2>
			<ul>
"""
	html = urllib2.urlopen('http://pairings.channelfireball.com/pairings/')
	soup = bs4.BeautifulSoup(html)
	form = cgi.FieldStorage()
	if 'name' in form:
		addevent(form['name'].value, form['url'].value if 'url' in form else '')
	with DeckDB() as db:
		events = {}
		for ev in db.get_events():
			events[ev[1]] = ev[2]

	for div in soup.find_all('div', class_='row'):
		for link in div.find_all('a'):
			name=link.get_text()
			target = link['href']
			if name in events:
				print "<li>Event %s already imported</li>" % name
			else:
				print "<li><a href='addevent?name=%s&amp;url=%s'>Import %s</a></li>" % (name, target, name)
	print """
	</ul>
	<h2>Add event from mtgpairings.com</h2>
	<ul>
"""
	html = urllib2.urlopen('http://mtgpairings.com/Event')
	soup = bs4.BeautifulSoup(html)
	for tr in soup.find_all('tr', onclick=re.compile('.*location.href.*')):
		tds = tr.find_all('td')
		name = "%s (%s, %s players)" % (tds[0].string.strip(), tds[1].string.strip(), tds[2].string.strip())
		target = 'http://mtgpairings.com'+re.sub(".*'(.*)'", r'\1', tr['onclick'])
		if name in events:
			print "<li>Event %s already imported</li>" % name
		else:
			print "<li><a href='addevent?name=%s&amp;url=%s'>Import %s</a></li>" % (name, target, name)
	print """
	</ul>
	<h2>Add an event from CFB API</h2>
	<ul>
"""
	shows = getCFBShows()
	for show in shows:
		print "<li><b>%s</b><ul>" % show.getName()
		for tournament in show.getTournaments():
			if tournament.getPairingsURL():
				if tournament.getName()+' at '+show.getName() in events:
					print "<li>%s already imported</li>" % (tournament.getName())
				else:
					print "<li><a href='addevent?name=%s&amp;url=%s'>Import %s</a></li>" % (tournament.getName()+'%20at%20'+show.getName(), tournament.getPairingsURL(), tournament.getName())
		print "</ul></li>"
	print """
	</ul>
	<h2>Add an event manually</h2>
	<p>Please request an event via dci@matthew.ath.cx</p>
"""

def main(args):
	addevent(args[0], args[1] if len(args) > 1 else '')

if __name__ == "__main__":
	
	if 'REQUEST_URI' in os.environ:
		cgitb.enable()
		output = HTMLOutput()
		docgi()
	else:
		if len(sys.argv) < 2:
			print "Usage: addevent <event> [<url>]"
			sys.exit(1)
		
		output = TextOutput()
		main(sys.argv[1:])

