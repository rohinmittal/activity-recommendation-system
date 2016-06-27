import json
from pymongo import MongoClient
client = MongoClient()
db = client.data

# find activities with time > 0
activities = db.data.find({})
categories = []
for each in activities:
	for cat in each["categories"]:
		categories.append(cat)

categories =  list(set(categories)) 
means = {}

for category in categories:
	#find same category activities with time > 0
	activityWithTime = db.data.find({"$and" : [ {"activityDuration" : {"$gt" : 0}} , {"categories" : {"$in" : [category]}}] } )
	sumSimilar = 0.0
	count = 0.0
	for each in activityWithTime:
		sumSimilar = sumSimilar + each["activityDuration"]
		count = count + 1.0
	if count != 0.0:
		means[category] = sumSimilar/count

activityWithNoTime = db.data.find({"activityDuration" : {"$eq" : 0} } )
for activity in activityWithNoTime:
	categories = activity["categories"]
	sumTime = 0.0
	for cat in categories:
		if cat not in means:
			continue
		sumTime = sumTime + means[cat]
	activityTime = sumTime/len(categories)
	db.data.update({"_id" : activity["_id"]}, {"$set" : {"activityDuration" : activityTime}})
	# update db with new time
