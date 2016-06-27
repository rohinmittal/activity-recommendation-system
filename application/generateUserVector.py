import numpy as np
#np.set_printoptions(precision=5, suppress=True)
import math
import string
import os
import operator, collections
from collections import OrderedDict

#import sys
#sys.setrecursionlimit(10000)

global max_score
max_score=5

def splitter(num_activities):
	global max_score
	allInd=np.arange(num_activities)
	intervals=max_score
	indices=np.linspace(np.min(allInd),np.max(allInd)+1,intervals+1)
	indices=np.array(indices,dtype='uint16')
	return indices

def generateUserVector(scoreDict, SubclusterDict):
	global max_score
	UserVectorsDict={}
	for cluster in SubclusterDict:
		ClusterOrder=SubclusterDict.get(cluster)
		score=scoreDict.get(cluster)
		intervals=splitter(len(ClusterOrder))
		IntervalOfInterest=max_score+1-score
		ub=intervals[IntervalOfInterest]-1
		lb=intervals[IntervalOfInterest-1]
		IntervalLength=ub-lb+1
		UVindex=int(math.ceil(IntervalLength/2))
		UVindex=lb+UVindex-1
		UserVectorsDict[cluster]=ClusterOrder[UVindex]
	return UserVectorsDict
