import urllib2, bs4

SWISSCUT='https://sixprizes.com/top-cut-calculator/'

def calculateTop8Threshold(playersPerBye, totalRounds, currentRound):

	currentRound = currentRound - 1
	effectivePlayers = 0
	for b in range(0, len(playersPerBye)):
		effectivePlayers = effectivePlayers + playersPerBye[b]*pow(2, b)

	maxOutstandingPoints = 3*(totalRounds-currentRound)

	html = urllib2.urlopen(SWISSCUT+'?players=%s&rounds=%s&cut=8' % (effectivePlayers, totalRounds))
	soup = bs4.BeautifulSoup(html)
	records = soup.find('ul', class_='').find_all("li")
	worst_record=records[-1].find('strong').get_text()
	wins=int(worst_record.split('-')[0])
	score=3*wins
	currentThreshold=score-maxOutstandingPoints
	return (currentThreshold, currentThreshold+3, currentRound*3)


#calculateTop8Threshold([1000, 300, 200, 100], 15, 10)
