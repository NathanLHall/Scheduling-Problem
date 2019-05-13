# -*- coding: utf-8 -*-
"""
Created on Thu Dec 13 01:51:01 2018

@author: NathanLHall
"""

PATH = "<path to output csv file>"

openTime = "7:30"
listTimes = []

def adjustTime(index):
    hour = int(openTime[0])
    half = int(openTime[2])

    hour += (index + 1) // 2
    half += 3 * ((index % 2))
    half = half % 6

    if half == 0:
        endHour = hour
        endHalf = 3
    else:
        endHour = hour + 1
        endHalf = 0

    if hour < 12:
        AMPM = "AM"
    elif hour == 12:
        AMPM = "PM"
    else:
        hour = hour % 12
        AMPM = "PM"

    start = str(hour) + ":" + str(half) + "0 " + AMPM

    if endHour < 12:
        AMPM = "AM"
    elif endHour == 12:
        AMPM = "PM"
    else:
        endHour = endHour % 12
        AMPM = "PM"

    end = str(endHour) + ":" + str(endHalf) + "0 " + AMPM

    return str(start) + " to " + str(end)


for i in range(27):
    start = adjustTime(i)
    listTimes.append(start)

for item in listTimes:
    print(item)


with open(PATH, 'w', newline = '\n') as file:
    week = ["", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    for day in week:
        file.write(day)
        file.write(',')
    file.write("Saturday")
    file.write("\n")
    for item in listTimes:
        file.write(item)
        file.write("\n")
