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
	cachedPairingsData = {}
	cachedDecklistData = {}

	@classmethod
	def getCachedPairingsData(cls, id, url):
		if not id in cls.cachedPairingsData:
			cls.cachedPairingsData[id] = getCFBJSONData(url) if url else None
		return cls.cachedPairingsData[id]

	@classmethod
	def getCachedDecklistData(cls, id, url):
		if not id in cls.cachedDecklistData:
			cls.cachedDecklistData[id] = getCFBJSONData(url)['data'] if url else None
		return cls.cachedDecklistData[id]
	
	def __init__(self, json):
		self.id=json['id']
		self.name=json['name']
		self.pairingsurl=json.get('pairings_url', None)
		self.decklistsurl=json.get('decklist_list_url', None)
	def getPairingsURL(self): return self.pairingsurl
	def getDecklistsURL(self): return self.decklistsurl
	def getName(self): return self.name
	def getId(self): return self.id
	def getRound(self):
		data = CFBTournament.getCachedPairingsData(self.id, self.pairingsurl)
		return int(data['current_round'])
	def getListURLForPlayer(self, name):
		data = CFBTournament.getCachedDecklistData(self.id, self.decklistsurl)
		for i in data:
			if i['name'] == name:
				return APIBASE+'/deck/raw/%s'%i['id']
		return None
	def getPlayersWithDecklists(self):
		data = CFBTournament.getCachedDecklistData(self.id, self.decklistsurl)
		return set([x['name'] for x in data])

	def getPairings(self):
		data = CFBTournament.getCachedPairingsData(self.id, self.pairingsurl)
		deckdata = CFBTournament.getCachedDecklistData(self.id, self.decklistsurl)
		roundnum=self.getRound()
		return [
			(roundnum, 
			 i['table'], 
			 (i['player']['name'], '', i['player']['points'])
			 ) for i in data['data']]


class CFBShow(object):
	def __init__(self, json):
		self.id=json['id']
		self.name=json['name']
		self.tournamenturl=json['url_tournament_list']
	def getName(self): return self.name
	def getID(self): return self.id
	def getTournaments(self):
		root = getCFBJSONData(self.tournamenturl)
		return [CFBTournament(x) for x in root['data'] if x['format'] != 'Package']

def getCFBShows(url='/api/json/'):
	root = getCFBJSONData(url)
	return [CFBShow(x) for x in root['data']]
