import numpy as np
np.set_printoptions(precision=5, suppress=True)
import math
import string
import os
import operator, collections
from collections import OrderedDict

import sys
sys.setrecursionlimit(10000)


def FloatScoreToInt(score):
	global max_score
	intervalLength=round(1/max_score,2)
	#print(intervalLength)
	separators=[0.00]
	ub=intervalLength
	while ub!=1:
		separators.append(ub)
		#print(separators)
		ub=round(ub+intervalLength,2)
		#print(ub)
	separators.append(1.00)
	if int(score)==1:
		return max_score
	decided_score=0
	temp_score=0
	for s in range(len(separators)):
		temp_score+=1
		if score>=separators[s] and score<separators[s+1]
			decided_score=temp_score
	if decided_score==0:
		print('Something went wrong while converting the score')
		return 1
	return decided_score

def tuneUserVector(ReviewScore, ReviewType, ClusterInContext, ReviewedActivityRank, ReviewedActivityID, SubclusterDict, CurrentUV):
	global max_score
	if ReviewType=='subjective':
		ReviewScore=FloatScoreToInt(ReviewScore)
	ScoreCombo=str(ReviewedActivityRank)+'->'+str(ReviewScore)
	
	#building MovementLength Map(some lists) based on (Rabk->Score) combos and deciding MovementLength
	Move1=['1->5','2->4','4->2','5->1']
	Move2=['1->x','2->x','3->x','4->x','5->x']
	Move3=['1->1','2->2','4->4','5->5']
	MovementLength=0
	if ScoreCombo in Move1:
		MovementLength=1
	elif ScoreCombo in Move3:
		MovementLength=3
	elif ScoreCombo=='3->3':
		MovementLength=random.choice([1,3])

	if MovementLength==0:
		ScoreCombo=ScoreCombo[:-1]+'x'
	if ScoreCombo in Move2:
		MovementLength=2

	#Finding if the ReviewedActivity is below or above the CurrentUV activity in the ClusterOrder
	ClusterOrder=SubclusterDict.get(ClusterInContext)
	UV_index=ClusterOrder.index(CurrentUV)
	Activity_index=ClusterOrder.index(ReviewedActivityID)
	is_below_UV='no'
	if Activity_index<=UV_index:
		is_below_UV='yes'

	#Deciding MovementDirection (0->DownTheOrder(towards the centroid i.e. 0th index); 1->UpTheOrder)
	MovementDirection=-1
	mid_score=math.ceil(max_score/2)
	if ReviewScore==mid_score:
		MovementDirection=random.randrange(0,2)
	elif ReviewScore<mid_score:
		if is_below_UV=='yes':
			MovementDirection=1
		else:
			MovementDirection=0
	elif ReviewScore>mid_score:
		if is_below_UV=='yes':
			MovementDirection=0
		else:
			MovementDirection=1

	if MovementDirection<0:
		print("Something went wrong with direction calculation!")

	#Calculate New UserVector
	NewUV_index=None
	NewUV=''
	if MovementDirection==0:
		NewUV_index=UV_index - MovementLength
	elif MovementDirection==1:
		NewUV_index=UV_index + MovementLength

	if NewUV_index==None:
		print("Something went wrong with direction calculation!")
		return CurrentUV

	if NewUV_index<0:
		NewUV_index=0
		print('Warning! Reached 0!')
	if NewUV_index>(len(ClusterOrder)-1):
		NewUV_index=len(ClusterOrder)-1
		print('Warning! Reached Max index!')

	NewUV=ClusterOrder[NewUV_index]
	return NewUV
