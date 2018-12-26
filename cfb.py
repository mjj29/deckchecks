import json, urllib2

APIBASE='https://test.playerlink.online'

def getCFBJSONData(url):
	html = urllib2.urlopen(APIBASE+url)
	root = json.loads(html.read())
	if not 'status' in root or not 'data' in root:
		raise Exception("Requesting CFB show list failed")
	if root['status'] != 'success':
		raise Exception("Requesting CFB show list returned failure")
	return root

class CFBTournament(object):
	def __init__(self, json):
		self.id=json['id']
		self.name=json['name']
		self.pairingsurl=json.get('pairings_url', None)
		self.data=None
	def getPairingsURL(self): return self.pairingsurl
	def getName(self): return self.name
	def getId(self): return self.id
	def getRound(self):
		if not self.data: self.data = getCFBJSONData(self.pairingsurl)
		return int(self.data['current_round'])
	def getPairings(self):
		if not self.data: self.data = getCFBJSONData(self.pairingsurl)
		roundnum=self.getRound()
		return [(roundnum, i['table'], (i['player']['name'], '', i['player']['points'])) for i in self.data['data']]


class CFBShow(object):
	def __init__(self, json):
		self.id=json['id']
		self.name=json['name']
		self.tournamenturl=json['url_tournament_list']
	def getName(self): return self.name
	def getID(self): return self.id
	def getTournaments(self):
		root = getCFBJSONData(self.tournamenturl)
		return [CFBTournament(x) for x in root['data']]

def getCFBShows(url='/api/json/'):
	root = getCFBJSONData(url)
	return [CFBShow(x) for x in root['data']]
