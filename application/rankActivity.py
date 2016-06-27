import math
import string
import os
import operator, collections
from collections import OrderedDict

#filtered activity list which needs to be ranked
def rankActivity(FilteredActivityList, CurrentUV, ClusterInContext, SubclusterDict):
	ClusterOrder=SubclusterDict.get(ClusterInContext)
	max_index=len(ClusterOrder)-1
	CurrentUV_index=ClusterOrder.index(CurrentUV)
	ActPosDict={}
	for activityID in FilteredActivityList:
		index=ClusterOrder.index(activityID)
		ActPosDict[index]=activityID
	ActPosDict_ordered = OrderedDict(sorted(ActPosDict.items()))
	ActivityList_Ordered=[]
	flag=0
	for index,activityID in ActPosDict_ordered.items():
		if(index<=CurrentUV_index):
			ActivityList_Ordered.append(activityID)
		elif flag==0:
			ActivityList_Ordered.reverse()
			ActivityList_Ordered.append(activityID)
			flag=1
		else:
			ActivityList_Ordered.append(activityID)
	if len(ActivityList_Ordered)!=len(FilteredActivityList):
		print('Wrong! Not all activities returned!')

	return ActivityList_Ordered
