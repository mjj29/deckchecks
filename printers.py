class NullTable:
	def __enter__(self):
		return self
	def __exit__(self, *args, **kwargs):
		pass
	def printRow(self, *args):
		print ", ".join([str(x) for x in args])

class Output:
	def getHeaders(self, maxrounds):
		headers = ["Name", "Score"]
		for i in range(1, maxrounds+1):
			headers.append("R%s" % i)
		headers.extend(["Build Table", "Previous Check(s)", "Check this round"])
		return headers
	def pageHeader(self, tournament, round):
		pass
	def table(self, *args):
		return NullTable()
	def printLink(self, link, text):
		pass
	def createButton(self, link, data, text):
		pass

class TextOutput(Output):
	def printPlayer(self, player, db, eventid):
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
	

class HTMLTable:
	def __init__(self, *args):
		self.titles = args
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
		print "<tr>"
		for a in args:
			print "<td>%s</td>" % a
		print "</tr>"


class HTMLOutput(Output):
	def table(self, *args):
		return HTMLTable(*args)
	def printPlayer(self, player, db, eventid):
		(name, score, tables, build) = player
		if 0 == build: build = "Bye"
		tablelinks = ""
		for t in tables:
			s = "<td>%s</td>" % t
			try:
				int(t)
				s = ("<td><a href='get_table?table=%s'>%s</a></td>" %(t,t))
			except: pass
			tablelinks = tablelinks + s

		prevChecks = db.getPreviousChecks(eventid, name)
		print "<tr><td><a href='get_player?name=%s'>%s</a></td><td>%s</td>%s<td><b><a href='get_table?table=%s'>%s</a></b></td><td>%s</td><td>" % (name, name, score, tablelinks, build, build, ", ".join([str(x) for x in prevChecks]))
		self.createButton('deckcheck', {'player':name}, 'Check this player')
		print "</td></tr>"

	def heading(self, text):
		print "<h3>%s</h3>" % text

	def printMessage(self, message):
		print "<p class='message'>%s</p>" % message

	def printComment(self, message):
		print "<!-- %s -->" % message

	def printLink(self, link, text):
		print "<p class='link'><a href='%s'>%s</a></p>" % (link, text)
	def createButton(self, link, data, text):
		print "<form action='%s'>" % link
		for k in data:
			print "<input type='hidden' name='%s' value='%s' />" % (k, data[k])
		print "<input type='submit' value='%s' /></form>" % (text)

	def pageHeader(self, tournament, round):
		print "<p class='menu'><b>%s, round %s</b> | <a href='get_table'>table</a> | <a href='get_player'>player</a> | <a href='top_tables'>top</a> | <a href='recommend'>recommend</a> | <a href='allchecks'>checks</a> | <a href='..'>change event</a></p>" % (tournament, round)
