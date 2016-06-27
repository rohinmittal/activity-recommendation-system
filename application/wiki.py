import json
import urllib, urllib2

def wikiInfo(activity_name):
	url = "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=" + urllib.quote_plus(activity_name) + "&srwhat=text&srprop=timestamp&continue=&format=json"
	response = json.loads(urllib.urlopen(url).read())
	if len(response['query']['search']) == 0:
		return ""
	return response['query']['search'][0]['title']
