class NullTable:
	def __enter__(self):
		return self
	def __exit__(self, *args, **kwargs):
		pass

class TextOutput:
	def printPlayer(self, player):
		(name, score, table, build) = player
		if 0 == build:
			print "%s (%s points, currently at %s) had byes" % (name, score, table)
		else:
			print "%s (%s points, currently at %s) build table %s" % (name, score, table, build)

	def printMessage(self, message):
		print str(message)
	
	def table(self, *args):
		return NullTable()

class HTMLTable:
	def __init__(self, *args):
		self.titles = args
	def __enter__(self):
		print "<table>"
		print "<tr>"
		for t in self.titles:
			print "<td>%s</td>" % t
		print "</tr>"
		return self
	def __exit__(self, *args, **kwargs):
		print "</table>"


class HTMLOutput:
	def table(self, *args):
		return HTMLTable(*args)
	def printPlayer(self, player):
		(name, score, table, build) = player
		if 0 == build: build = "bye"
		print "<tr><td>%s</td><td>%s</td><td>%s</td><td><b>%s</b></td></tr>" % (name, score, table, build)

	def printMessage(self, message):
		print "<p>%s</p>" % message

