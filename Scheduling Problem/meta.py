# -*- coding: utf-8 -*-
"""
Created on Fri Dec 21 11:44:45 2018

@author: nathan
"""

import mathSchedule_v2
from drawnow import *
import matplotlib.pyplot as plt
import statistics
import time

crossoverRate = 0.98
coinFlip = 0.5
num_slots = 132
maxGens = 20000
populationSize = 5
mutationRate = 1.0/num_slots
report = False
scoreToBeat = -99999

experiments = 50

data = []
genScoreData = []
for i in range(experiments):
    print("Experiment", i + 1)
    start = time.time()
    score, genScores = mathSchedule_v2.main(num_slots, populationSize, crossoverRate, mutationRate, coinFlip, report, scoreToBeat)
    genScoreData.append(genScores)
    end = time.time()
    runtime = end - start
    data.append(score)

totalSpanData = []
for member in genScoreData:
    spanData = []
    span = 0
    fitness = member[0][1]
    for i in range(1, len(member)):
        if fitness == member[i][1]:
            span += 1
        else:
            spanData.append(span)
            span = 0
        fitness = member[i][1]
    totalSpanData.append(spanData)

plt.ion()
for spanData in totalSpanData:
    def makeFig():
        plt.plot(spanData, 'ro-')
        return None

    drawnow(makeFig)


data.sort()
bestScore = -99999
mean = statistics.mean(data)
median = statistics.median(data)
mode = statistics.mode(data)
midrange = (data[0] + data[-1]) / 2
print()
for entry in data:
    if entry > bestScore:
        bestScore = entry[0]

print("Best Score:", bestScore)
print("Minimum:", data[0])
print("Maximum:", data[-1])
print("Mean:", mean)
print("Median:", median)
print("Mode:", mode)
print("Midrange:", midrange)
