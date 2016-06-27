from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from pymongo import MongoClient
import json, urllib, urllib2
from sentiment import findSentiment 

from wiki import wikiInfo
from rankActivity import rankActivity
from generateUserVector import generateUserVector

from unidecode import unidecode

from application import app, db, classifier
import random

_key = "AIzaSyBkIfX7TvwEDWKwETzlmSk-GWnacPBD2QM"
app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'

moods = {"Feeling Outdorsy" : "1", "Feeling Artsy" : "2", "Feeling hungry or thirsty" : "3", "Feeling Shopaholic" : "4", "Feeling Touristy" : "5"}
modes = ["driving", "bicycling", "walking", "transit"]

##### create dictionary for initial questions
f = open('./files/subClusters.txt').read()
subClusters = {}
splitClusters = f.split('\n')
for each in splitClusters:
	each = each.replace('\'', '')
	each = each.replace('[', '')
	each = each.replace(']', '')
	each = each.replace(' ', '')
	eachCluster = each.split(":")
	if len(eachCluster[0]) == 0:
		continue
	cluster_num = "cluster" + str(eachCluster[0])
	keys = eachCluster[1].split(",")
	subClusters[cluster_num] = keys

##### for user profiling #####
clusterDict = {}
for key in moods:
	cluster = {}
	cluster_num = "cluster" + str(moods[key])
	activities = db.data.find({"cluster_num" : moods[key]})
	for activity in activities:
		cluster[activity["activityID"]] = activity["activity_vector"]
	clusterDict[cluster_num] = cluster 

####################### ACTIVITY SCHEMA (db.data) ###################
# _id : 
#features : []
#activityDuration : 
#totalTime : 
#address :
#category : 
#title : 
#image_url :
#location :
#all_categories :
#review_url :
#reviews : [{
#		text : 
#		sentiment :
#		username :
#	}]
###########################################################

####################### USER SCHEMA (db.user) ###################
#username:
#password:
#reviews: [{
#		 text:
#		sentiment:
#	 }]
###########################################################

######## logout module
@app.route('/logout/')
def logout():
	session.clear()
	return redirect(url_for('login'))

######## login module
@app.route('/', methods=['POST', 'GET'])
@app.route('/login/', methods=['POST', 'GET'])
def login():
	#login form will go here
	if len(session) != 0:
		return redirect(url_for('logout'))

	error = ""
	if request.method == 'POST':
		if valid_login(request.form['username'], request.form['password']):
			sumSessionCounter()
			session['name'] = request.form['username']
			return redirect(url_for('home'))
		else:
			error = "Invalid Credentials"

	return render_template('login.html', error=error) 

######## signup module
@app.route('/signup/', methods=['POST', 'GET'])
def signup():
	#signup form will go here
	error = ""
	if request.method == 'POST':
		if request.form['username'] != "" and request.form['password'] == request.form['repassword']:
			if db.users.find_one({"username" : request.form['username']}) == None:
				#add to mongodb
				sumSessionCounter()
				session['name'] = request.form['username']
				preferences = {"cluster1" : "", "cluster2" : "", "cluster3" : "", "cluster4" : "", "cluster5" : ""}
				db.users.insert_one({"username" : request.form['username'], "password" : request.form["password"], "reviews" : [], "preferences" : preferences})
				return redirect(url_for('questions'))
		
		error = "Invalid Credentials"
	return render_template('signup.html', error=error) 

####### questions for first time users
@app.route('/questions/', methods=['POST', 'GET'])
def questions():
	if len(session) == 0:
		return redirect(url_for('login'))
		
	error = ""
	if request.method == 'POST':
		# take user preference
		cluster1 = request.form['cluster1']	
		cluster2 = request.form['cluster2']	
		cluster3 = request.form['cluster3']	
		cluster4 = request.form['cluster4']	
		cluster5 = request.form['cluster5']	
		userPref = {"cluster1" : int(cluster1), "cluster2" : int(cluster2), "cluster3" : int(cluster3), "cluster4" : int(cluster4), "cluster5" : int(cluster5)}
		print "User's Initial Rating"
		print userPref
		preferences = generateUserVector(userPref, subClusters)
    		print "User Preferences"
    		print preferences
		db.users.update({"username" : session['name']}, {"$set" : {"preferences" : preferences}})
		return redirect(url_for('home'))

	questions = {}
	for each in subClusters:
		response = db.data.find_one({"activityID" : subClusters[each][0]})
		questions[each] = {"title" : response['title'], "categories" : response["categories"], "image_url" : response["image_url"]}
	return render_template('questions.html', error=error, questions=questions)

####### home module
@app.route('/home/', methods=['POST', 'GET'])
def home():
	#goes to get method first time. Gets the location
	#reaches post method, but this time 'location' is stepOne... so shows user a map and fields for imput data.
	#now, when user clicks on submit, 'location' is stepTwo, so gets redirected to query
	if len(session) == 0:
		return redirect(url_for('login'))

	error = ""
	if request.method == 'POST':
		lat = request.form['latitude']
		lng = request.form['longitude']
		mood = request.form['mood']
		mode = request.form['mode']
		time = request.form['time']
		location = request.form['location']
		if time == "":
			error = "Invalid Arguments"
			return render_template('home.html', error=error, lat=lat, lng=lng, modes=modes, moods=moods)
			
		if location != "":
			#find lng/lat using google api
			lat, lng = googleGeocode(location)
		return redirect('/query/50/' + str(lat) + '/' + str(lng) + '/' + mode + '/' + time + '/' + mood)

	return render_template('home.html', error=error, lat=0, lng=0, modes=modes, moods=moods)

######## query for activities within radius
@app.route("/query/<distance>/<lat>/<lng>/<mode>/<time>/<moodID>/", methods=['GET', 'POST'])
def main(distance, lat, lng, mode, time, moodID):
	if len(session) == 0:
		return redirect(url_for('login'))

	if request.method == 'POST':
		return redirect(url_for('home'), code=307)

	response = queryDB(float(lat), float(lng), float(distance), moods[moodID])
	origin = str(lat) + "," + str(lng)
	userResults = json.loads(googleDistanceMatrix(origin, mode, int(time), response))

	userFilteredActivities = [activity["activityID"] for activity in userResults]

	cluster_num = "cluster" + str(moods[moodID])
	user_vector = db.users.find_one({"username" : session["name"]})
	user_vector = user_vector["preferences"][cluster_num]

	print "Search as per current user pref: " + "---cluster_num---" + str(cluster_num) + "---activity---" + str(user_vector)
    	print "ranked activities"
	rankedActivities = rankActivity(userFilteredActivities, user_vector, cluster_num, subClusters)
	print rankedActivities

	results = []
	for ID in rankedActivities:
		for activity in userResults:
			if activity["activityID"] != ID:
				continue
			results.append(activity)
		
	#render this json to final view (on javascript maybe)	
	return render_template('home.html', results=results, lat=lat, lng=lng, modes=modes, moods=moods)

####### activity details
@app.route('/activity/<id>/', methods=['GET', 'POST'])
def activity(id):
	if len(session) == 0:
		return redirect(url_for('login'))

	activity = db.data.find_one({"_id" : int(id)})
	title = activity["title"]
	wikiurl = ""
	wikiname = wikiInfo(title)
	if wikiname != "":
		wikiurl = "https://en.wikipedia.org/wiki/" + wikiname.replace(" ", "_")
	
	if request.method == 'POST':
		text = request.form['reviewText']
		sentiment = findSentiment(classifier, text)
		username = session["name"]

		data = {"text" : text, "sentiment" : sentiment, "username" : username}
		user_data = {"text" : text, "sentiment" : sentiment, "activity" : title}
		db.data.update({"_id" : int(id)}, {"$push" : {"reviews" : data}})
		db.users.update({"username" : username}, {"$push" : {"reviews" : user_data}})
		
		activity = db.data.find_one({"_id" : int(id)})

		clusterInContext = "cluster" + activity["cluster_num"]
		reviewedActivityID = activity["activityID"]
		user_vector = db.users.find_one({"username" : session["name"]})
		user_vector = user_vector["preferences"][clusterInContext]
#		UserVectorTune(sentiment, clusterInContext, reviewedActivityID, clusterDict, user_vector, centroidDict[clusterInContext])

	return render_template('activity.html', activity=activity, wikiurl=wikiurl)

####### user profile 
@app.route('/user/<username>/', methods=['GET'])
def user(username):
	if len(session) == 0:
		return redirect(url_for('login'))

	user = db.users.find_one({"username" : username})
	return render_template('user.html', user=user, db=db) 

################################################################################
#### additional modules (not views)
################################################################################

def sumSessionCounter():
	try:
		session['counter'] += 1
	except KeyError:
		session['counter'] = 1

######## validate login credentials
def valid_login(username, password):
	result = db.users.find_one({"username" : username})
	if result == None:
		return False
	if result['password'] == password:
		return True
	return False

def queryDB(lng, lat, distance, mood):
	response = db.data.find( { "$and" : [ {"location": { "$geoWithin": { "$centerSphere": [ [lng, lat], distance/3963.2] } }}, {"cluster_num" : mood}] } )
	result = [res for res in response]
	return result

def googleDistanceMatrix(origin, mode, time, activities):
	#activities is coming from mongodb query
	if len(activities) == 0:
		return json.dumps([])

	destination = ""
	activityIDs = []
	for activity in activities:
		destination = destination + str(activity["location"][0]) + "," + str(activity["location"][1]) + "|"
		activityIDs.append(activity["_id"])
	
	destination = destination[:-1]
	url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins=" + origin + "&destinations=" + destination + "&mode=" + mode + "&key=" + _key
	print url

	response = json.loads(urllib2.urlopen(url).read())

	for ID in range(len(response["rows"][0]["elements"])):
		tDuration = response["rows"][0]["elements"][ID]["duration"]["text"].split()
		actID = db.data.find_one({"title" : activities[ID]["title"]})["_id"]

		if len(tDuration) == 4:
			#something like 4 hours 30 minutes
			totalTime = 0
			if tDuration[1] == "days" or tDuration[1] == "day":
				totalTime = totalTime + (int(tDuration[0])*3600)
			elif tDuration[1] == "hours" or tDuration[1] == "hour":
				totalTime = totalTime + (int(tDuration[0])*60)

			if tDuration[3] == "hours" or tDuration[3] == "hour":
				totalTime = totalTime + (int(tDuration[2])*60)
			elif tDuration[3] == "mins" or tDuration[3] == "min":
				totalTime = totalTime + (int(tDuration[2]))

			totalTime = totalTime + activities[ID]["activityDuration"]
			db.data.update({"_id" : actID}, {"$set" : {"totalTime" : totalTime}})
		else:
			totalTime = int(tDuration[0]) + activities[ID]["activityDuration"]
			#db.data.update({"title":activities[ID]["title"]}, {"$set" : {"totalTime" : totalTime}})
			db.data.update({"_id" : actID}, {"$set" : {"totalTime" : totalTime}})

	filteredActivities = db.data.find({"$and": [ {"totalTime" : {"$lt" : time}}, {"_id" : {"$in": activityIDs }} ] })

	result = []
	for activity in filteredActivities:
		alreadyReviewed = False
		for review in activity["reviews"]:
			if review["username"] == session["name"]:
				alreadyReviewed = True
		image_url = url_for('static', filename='images/default.gif')
		if "http" in activity["image_url"]:
			image_url = activity["image_url"]
		result.append({"id" : activity["_id"], "address" : activity["address"], "activityDuration" : activity["activityDuration"], "totalTime" : activity["totalTime"], "title" : activity["title"], "image_url" : image_url, "location" : activity["location"], "alreadyReviewed" : alreadyReviewed, "activity_vector" : activity["activity_vector"], "activityID" : activity["activityID"]})			
	return json.dumps(result)

def googleGeocode(address):
	url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + urllib.quote_plus(unidecode(address)) + "&key=" + _key
	response = json.loads(urllib2.urlopen(url).read())
	lat = response["results"][0]["geometry"]["location"]["lat"]
	lng = response["results"][0]["geometry"]["location"]["lng"]
	return lat, lng
