import re
from cfb import CFBTournament

class NullTable:
	def __enter__(self):
		return self
	def __exit__(self, *args, **kwargs):
		pass
	def printRow(self, *args):
		print ", ".join([str(x) for x in args])
	def setNextRowType(self, _): pass

class Output:
	def getHeaders(self, maxrounds):
		headers = ["Name", "Score"]
		for i in range(1, maxrounds+1):
			headers.append("R%s" % i)
		headers.extend(["Build Table", "Previous Check(s)", "Check this round"])
		return headers
	def pageHeader(self, tournament, round, form):
		pass
	def table(self, *args):
		return NullTable()
	def printLink(self, form, link, text):
		return self.makeLink(form, link, text)
	def makeLink(self, form, link, text):
		return text
	def createButton(self, form, link, data, text):
		pass

class TextOutput(Output):
	def printPlayer(self, player, db, eventid, form, newbutton=None):
		(name, score, table, build) = player
		if 0 == build:
			print "%s (%s points, tables %s) had byes" % (name, score, table)
		else:
			print "%s (%s points, tables %s) build table %s" % (name, score, table, build)

		prevChecks = db.getPreviousChecks(eventid, name)

		if 0 == len(prevChecks):
			print "%s has not previously been checked" % name
		else:
			print "%s was checked in rounds %s" % (name, ", ".join([str(x) for x in prevChecks]))

	def printMessage(self, message):
		print str(message)

	def printComment(self, message):
		print str(message)

	def heading(self, text):
		print text
		print "----------------"
	
def remove_tags(string):
	return re.sub('<[^>]*>', '', string)

class TSVTable:
	def __init__(self, *args):
		self.titles = args
	def __enter__(self):
		print "\t".join([str(x) for x in self.titles])
		return self
	def __exit__(self, *args, **kwargs):
		pass
	def printRow(self, *args):
		print "\t".join([remove_tags(str(x)) for x in args])
	def setNextRowType(self, _): pass

class TSVOutput(Output):
	def table(self, *args):
		return TSVTable(*args)
	def printPlayer(self, player, db, eventid, form, newbutton=None):
		(name, score, tables, build) = player
		if 0 == build: build = "Bye"

		prevChecks = db.getPreviousChecks(eventid, name)
		print "\t".join([str(x) for x in [name, score]+tables+[build,", ".join([str(x) for x in prevChecks])]])

	def heading(self, text):
		print text

	def printMessage(self, message):
		print message

	def printComment(self, message):
		print "# %s"%text

	def createButton(self, form, link, data, text):
		pass

	def pageHeader(self, tournament, round, form):
		pass

class HTMLTable:
	def __init__(self, *args):
		self.titles = args
		self.nextRowType = ''
	def __enter__(self):
		print "<table>"
		print "<tr>"
		for t in self.titles:
			print "<th>%s</th>" % t
		print "</tr>"
		return self
	def __exit__(self, *args, **kwargs):
		print "</table>"
	def printRow(self, *args):
		print "<tr class='%s'>"%self.nextRowType
		for a in args:
			print "<td>%s</td>" % a
		print "</tr>"
		self.nextRowType = ''
	def setNextRowType(self, rowType):
		self.nextRowType=rowType


class HTMLOutput(Output):
	def table(self, *args):
		return HTMLTable(*args)
	def printPlayer(self, player, db, eventid, form, newbutton=None):
		(name, score, tables, build, deckid) = player
		if 0 == build: build = "Bye"
		tablelinks = ""
		for t in tables:
			s = "<td>%s</td>" % t
			try:
				int(t)
				s = ("<td>"+self.makeLink(form, 'get_table?table=%s'%t, t)+"</td>")
			except: pass
			tablelinks = tablelinks + s

		prevChecks = db.getPreviousChecks(eventid, name)
		print "<tr><td>"
		print self.makeLink(form, 'get_player?name=%s'%name, name)
		print "<td>%s</td>%s<td><b>"%(score, tablelinks)
		print self.makeLink(form, 'get_table?table=%s'%build, build)
		listurl = db.getDecklistUrl(eventid)
		if listurl and deckid:
			print " [<a href='%s/%s'>online</a>]" % (listurl, deckid)
		print "</b></td><td>%s</td><td>" % (", ".join([str(x) for x in prevChecks]))
		if db.isEventTeam(eventid):
			self.createButton(form, 'deckcheck', {'player':name, 'seat':'0'}, 'Check Seat A')
			self.createButton(form, 'deckcheck', {'player':name, 'seat':'1'}, 'Check Seat B')
			self.createButton(form, 'deckcheck', {'player':name, 'seat':'2'}, 'Check Seat C')
		else:
			self.createButton(form, 'deckcheck', {'player':name}, 'Check this player')

		if newbutton:
			print "</td><td>"
			(table, options, text) = newbutton
			self.createButton(form, table, options, text)
		print "</td></tr>"

	def heading(self, text):
		print "<h3>%s</h3>" % text

	def printMessage(self, message):
		print "<p class='message'>%s</p>" % message

	def printComment(self, message):
		print "<!-- %s -->" % message

	def makeLink(self, form, link, text):
		l = "<form id='%s' action='%s' method='post'>" % (link, link)
		l = l + "<input type='hidden' name='password' value='%s'/>" % (form['password'].value if 'password' in form else '')
		l = l + "</form>"
		l = l + "<a href='#' onclick=\"document.getElementById('%s').submit();\">%s</a>"% (link, text)
		return l
	def printLink(self, form, link, text):
		print "<p class='link'>"+self.makeLink(form, link, text)+"</p>" 
	def createButton(self, form, link, data, text):
		print "<form action='%s'>" % link
		print "<input type='hidden' name='password' value='%s'/>" % (form['password'].value if 'password' in form else '')
		for k in data:
			print "<input type='hidden' name='%s' value='%s' />" % (k, data[k])
		print "<input type='submit' value='%s' /></form>" % (text)

	def pageHeader(self, db, tournament, round, form):
		tournament = db.getEventName(db.getEventId(tournament))
		print "<div class='menu'><b>%s, round %s</b> | " % (tournament, round)
		print self.makeLink(form, 'get_table', 'table')
		print " | "
		print self.makeLink(form, 'get_player', 'player')
		print " | "
		print self.makeLink(form, 'top_tables', 'top')
		print " | "
		print self.makeLink(form, 'recommend', 'recommend')
		print " | "
		print self.makeLink(form, 'allchecks', 'checks')
		print " | "
		print self.makeLink(form, 'pairings', 'pairings')
		print " | "
		print self.makeLink(form, 'import', 'update')
		print " | "
		print self.makeLink(form, 'settings', 'settings')
		print " | <a href='..'>change event</a></div>"

