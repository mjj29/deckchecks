class NullTable:
	def __enter__(self):
		return self
	def __exit__(self, *args, **kwargs):
		pass
	def printRow(self, *args):
		print ", ".join([str(x) for x in args])

class TextOutput:
	def printPlayer(self, player, db, eventid):
		(name, score, table, build) = player
		if 0 == build:
			print "%s (%s points, currently at %s) had byes" % (name, score, table)
		else:
			print "%s (%s points, currently at %s) build table %s" % (name, score, table, build)

		prevChecks = db.getPreviousChecks(eventid, name)

		if 0 == len(prevChecks):
			print "%s has not previously been checked" % name
		else:
			print "%s was checked in rounds %s" % (name, ", ".join([str(x) for x in prevChecks]))

	def printMessage(self, message):
		print str(message)

	def heading(self, text):
		print text
		print "----------------"
	
	def table(self, *args):
		return NullTable()

	def printLink(self, link, text):
		pass

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


class HTMLOutput:
	def table(self, *args):
		return HTMLTable(*args)
	def printPlayer(self, player, db, eventid):
		(name, score, table, build) = player
		if 0 == build: build = "bye"

		prevChecks = db.getPreviousChecks(eventid, name)
		print "<tr><td>%s</td><td>%s</td><td>%s</td><td><b>%s</b></td><td>%s</td></tr>" % (name, score, table, build, ", ".join([str(x) for x in prevChecks]))

	def heading(self, text):
		print "<h3>%s</h3>" % text

	def printMessage(self, message):
		print "<p>%s</p>" % message

	def printLink(self, link, text):
		print "<p><a href='%s'>%s</a></p>" % (link, text)
