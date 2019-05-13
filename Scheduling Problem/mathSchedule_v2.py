# -*- coding: utf-8 -*-
"""
Created on Sat Dec 15 04:17:06 2018

@author: NathanLHall
"""

import copy
import csv
from drawnow import *
import math
import matplotlib.pyplot as plt
import os
import random
import time

# =============================================================================
# User Variables
# =============================================================================

# User, you can make changes to these variables, as you see fit

#Folder location to find tutor availability schedules
availabilityPATH = "\\\\192.168.0.3\\NateFiles\\Science\\Computer Science\\Scheduling Problem\\Tutor Availabilities\\"
templatePATH = "\\\\192.168.0.3\\NateFiles\\Science\\Computer Science\\Scheduling Problem\\Template.csv"
payrollPATH = "\\\\192.168.0.3\\NateFiles\\Science\\Computer Science\\Scheduling Problem\\Weekly Payroll.csv"
mathSchedulePATH = "\\\\192.168.0.3\\NateFiles\\Science\\Computer Science\\Scheduling Problem\\Weekly Schedule.csv"
notesPATH = "\\\\192.168.0.3\\NateFiles\\Science\\Computer Science\\Scheduling Problem\\Notes.txt"

# Running from Ubuntu
#availabilityPATH = "/run/user/1000/gvfs/smb-share:server=192.168.0.3,share=natefiles/Science/Computer Science/Scheduling Problem/Tutor Availabilities/"
#templatePATH = "/run/user/1000/gvfs/smb-share:server=192.168.0.3,share=natefiles/Science/Computer Science/Scheduling Problem/Template.csv"
#payrollPATH = "/run/user/1000/gvfs/smb-share:server=192.168.0.3,share=natefiles/Science/Computer Science/Scheduling Problem/Weekly Payroll.csv"
#mathSchedulePATH = "/run/user/1000/gvfs/smb-share:server=192.168.0.3,share=natefiles/Science/Computer Science/Scheduling Problem/Weekly Schedule.csv"
#notesPATH = "/run/user/1000/gvfs/smb-share:server=192.168.0.3,share=natefiles/Science/Computer Science/Scheduling Problem/Notes.txt"



# Number of desired tutors to be on duty during each time slot
onDuty = [1,1,2,2,2,2,2,3,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2,2,1,1, # Monday
          1,1,2,2,2,2,2,3,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2,2,1,1, # Tuesday
          1,1,2,2,2,2,2,3,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2,2,1,1, # Wednesday
          1,1,2,2,2,2,2,3,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2,2,1,1, # Thursday
          1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,                       # Friday
          1,1,1,1,1,1,1,1]

# =============================================================================
# Not User Variables
# =============================================================================

tutorDict = {}
plt.ion()
ys = []

#Index of where the start of the workday is located in the schedule array
monIndex = 0
tueIndex = 27
wedIndex = 54
thuIndex = 81
friIndex = 108
satIndex = 124
dayIndexes = [monIndex, tueIndex, wedIndex, thuIndex, friIndex, satIndex]
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

#Maximum number of half-hour slots there are in any given workday
max_slots = 27

#Number of half-hour slots during other days
fri_slots = 16
sat_slots = 8

#Number of half-hour slots that Saturday morning doesn't have compared to other mornings
offset = 5



#==============================================================================
# File Reading/Writing Functions
#==============================================================================

def get_availability(filename):
    contents = []
    with open(availabilityPATH + filename + ".csv", newline='\n') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            contents.append(row)
        desired_hours = float(contents[0][0])

    # Clear the day and time entries
    contents.pop(0)
    for row in contents:
        row.pop(0)

    # Copy 0, 1, 2 entries from the tutor's availability file
    schedule =[]
    for i in range(6):
        for j in range(27):
            if contents[j][i] != '':
                schedule.append(int(contents[j][i]))

    # Count the number of hours they have marked as available
    hoursAvailable = 0
    for i in range(6):
        for j in range(27):
            if contents[j][i] != 0:
                hoursAvailable += 0.5

    # Double check if the number of requested hours is greater than the number
    # of hours they have marked available
    if desired_hours > hoursAvailable:
        desired_hours = hoursAvailable

    # Save formatted scheule to dictionary
    tutorDict[filename] = schedule

    return schedule, desired_hours

def createSlotEntry(index, day, shiftNames, actualOnDuty):
    entry = ''
    for i in range(len(shiftNames[day + index])):
        entry += shiftNames[day + index][i]
        if i < actualOnDuty[day + index] - 1:
            entry += ' '
        else:
            entry += ','
    return entry

def createRow(index, shiftNames, actualOnDuty):
    entries = ''
    for day in dayIndexes:
        if index in range(offset, offset + sat_slots):
            if day != satIndex:
                entry = createSlotEntry(index, day, shiftNames, actualOnDuty)
            else:
                entry = createSlotEntry(index - 5, day, shiftNames, actualOnDuty)
        elif index in range(offset) or index in range(offset + sat_slots, fri_slots):
            if day != satIndex:
                entry = createSlotEntry(index, day, shiftNames, actualOnDuty)
            else:
                continue
        else:
            if day < friIndex:
                entry = createSlotEntry(index, day, shiftNames, actualOnDuty)
            else:
                continue

        entries += entry
    entries += '\n'
    return entries

def exportSchedule(schedule, actualOnDuty):
    shiftNames = []
    for i in range(len(schedule)):
        tutorsOnDuty = schedule[i]
        firstNames = []
        for name in tutorsOnDuty:
            index = name.index(',')
            firstName = name[index + 2:]
            firstNames.append(firstName)
        shiftNames.append(firstNames)

    for i in range(len(shiftNames)):
        shiftNames[i] = sorted(shiftNames[i])

    contents = []
    with open(templatePATH, newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter = ',')
        for row in csv_reader:
            contents.append(row)
    # Remove header ("MONDAY", "TUESDAY", ...)
    contents.pop(0)

    times = []
    for i in range(len(contents)):
        times.append(contents[i][0])

    with open(mathSchedulePATH, 'w', newline = '\n') as file:
        file.write(', MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY\n')

        for i in range(max_slots):
            file.write(times[i] + ',')
            row_contents = createRow(i, shiftNames, actualOnDuty)
            file.write(row_contents)
    return None

def exportPayrollData(schedule, tutorDict, tutors):
    #Set initial number of scheduled hours to 0
    for tutor in tutors:
        tutorDict[str(tutor) + ": Scheduled"] = 0

    for shift in schedule:
        for tutor in shift:
            tutorDict[str(tutor) + ": Scheduled"] += 0.5

    with open(payrollPATH, 'w', newline = '\n') as file:
        file.write("LAST NAME,FIRST NAME,HOURS WORKED\n")
        for tutor in tutors:
            file.write(str(tutor) + ',' + str(tutorDict[str(tutor) + ": Scheduled"]) + '\n')
    return None

def exportNotes(schedule, tutorDict, tutors, dayIndexes):
    notes = []
    for tutor in tutors:
        fixes = []
        for i in range(len(schedule)):
            condition = False
            AMPM = "AM"
            # Check if tutor is assigned to a single half-hour shift
            if tutor in schedule[i]:

                # If index is for the first slot, only check forward for consecutive assignment
                if (i % 27 == 0 or i == 124) and tutor not in schedule[i + 1]:
                    condition = True

                # If index is not an opening or closing slot, check forward and backward for consecutive assignment
                elif (i % 27 > 0 and i % 27 < 26 and i < 123) and (tutor not in schedule[i - 1] and tutor not in schedule[i + 1]):
                    condition = True

                # If index is for the last slot in the day, only check backward for consecutive assignment
                elif (i % 27 == 26 or i == 123 or i == 131) and tutor not in schedule[i - 1]:
                    condition = True

                if condition == True:
                    for j in range(len(dayIndexes)):
                        startHour = 7 # Hour of when the opening shift starts
                        startMin = 1 # If opening shift starts at 7:30, then adjust for this half hour
                        if i < 108:
                            shiftsInDay = 27
                        elif i >= 108 and i < 124:
                            shiftsInDay = 16
                        else:
                            shiftsInDay = 8
                            startHour = 10
                            startMin = 0

                        if i in range(dayIndexes[j] + shiftsInDay):
                            day = days[j]
                            slot = i - dayIndexes[j]
                            hour = int(startHour + (slot // 2) + (slot % 2))
                            if hour >= 12:
                                AMPM = "PM"
                                if hour > 12:
                                    hour = hour % 12
                            minute = int((slot + startMin % 2) * 30)
                            if minute == 0:
                                minute = str(minute) + '0'
                            fixes.append("index: " + str(i) + " " + str(day) + " - " + str(hour) + ":" + str(minute) + " " + AMPM)
                            break
        if len(fixes) == 0:
            notes.append(str(tutor) + ":" +
             "\n\tRequested Hours: " + str(tutorDict[str(tutor) + ': Original Request']) +
             "\n\tScaled Requested Hours: " + str(tutorDict[str(tutor) + ": Requested"]) +
             "\n\tScheduled Hours: " + str(tutorDict[str(tutor) + ": Scheduled"]) +
             "\n\tDifference: " + str(tutorDict[str(tutor) + ": Scheduled"] - (tutorDict[str(tutor) + ": Original Request"])) +
             "\n\tScaled Difference: " + str(tutorDict[str(tutor) + ": Scheduled"] - (tutorDict[str(tutor) + ": Original Request"])) + " hrs\n\n")

        if len(fixes) > 0:
            notes.append(str(tutor) + ":" +
             "\n\tRequested Hours: " + str(tutorDict[str(tutor) + ': Original Request']) +
             "\n\tScaled Requested Hours: " + str(tutorDict[str(tutor) + ": Requested"]) +
             "\n\tScheduled Hours: " + str(tutorDict[str(tutor) + ": Scheduled"]) +
             "\n\tDifference: " + str(tutorDict[str(tutor) + ": Scheduled"] - (tutorDict[str(tutor) + ": Original Request"])) +
             "\n\tScaled Difference: " + str(tutorDict[str(tutor) + ": Scheduled"] - (tutorDict[str(tutor) + ": Original Request"])) + " hrs" +
                "\n\t" + str(len(fixes)) + " 30min shifts assigned:")
            for i in range(len(fixes)):
                notes.append("\n\t\t" + fixes[i])
            notes.append("\n\n")

    with open(notesPATH, 'w') as file:
        for i in range(len(notes)):
            file.write(notes[i])

    return None



# =============================================================================
# GA Function Definitions
# =============================================================================
def objective(individual, tutorDict, tutors):
    fitness = 0

    # Searching in the left direction of the schedule isn't allowed
    leftClosed = [0, 2, 27, 29, 54, 56, 81, 83, 108, 110, 124]
    # Searching in the right direction of the schedule isn't allowed
    rightClosed = [24, 26, 51, 53, 78, 80, 105, 107, 123, 131]

    #Check for shift assignments that are less than 2 hours long
    for i in range(len(individual.schedule)):
        for name in individual.schedule[i]:


            # Opening shifts
            if i in leftClosed and i % 27 == 0:
                if name not in individual.schedule[i + 1]:
                    fitness -= 90
                if name not in individual.schedule[i + 2]:
                    fitness -= 30
                if name not in individual.schedule[i + 3]:
                    fitness -= 10
            # This may seem redundant, but it helps prevent a double penalty on
            # the opening tutor, where this is intended only for the tutor that
            # comes in an hour after opening
            elif i in leftClosed and i % 27 == 2:
                if name not in individual.schedule[i + 1]:
                    fitness -= 90
                if name not in individual.schedule[i + 2]:
                    fitness -= 30
                if name not in individual.schedule[i + 3]:
                    fitness -= 10

            # Closing shifts
            elif i in rightClosed and (i % 27 == 26 or i % 27 == 15 or i % 27 == 23):
                if name not in individual.schedule[i - 1]:
                    fitness -= 90
                if name not in individual.schedule[i - 2]:
                    fitness -= 30
                if name not in individual.schedule[i - 3]:
                    fitness -= 10
            # This is for the tutor who leaves an hour before closing
            elif i in rightClosed and (i % 27 == 24):
                if name not in individual.schedule[i - 1]:
                    fitness -= 90
                if name not in individual.schedule[i - 2]:
                    fitness -= 30
                if name not in individual.schedule[i - 3]:
                    fitness -= 10

            # All other shifts
            elif i > 3 and i < len(individual.schedule) - 4:
                if name not in individual.schedule[i - 3]:
                    if name not in individual.schedule[i - 2]:
                        if name not in individual.schedule[i - 1]:
                            if name not in individual.schedule[i + 1]:
                                fitness -= 90
                            if name not in individual.schedule[i + 2]:
                                fitness -= 30
                            if name not in individual.schedule[i + 3]:
                                fitness -= 10
                        else:
                            if name not in individual.schedule[i + 1]:
                                fitness -= 90
                            if name not in individual.schedule[i + 2]:
                                fitness -= 30
                    else:
                        if name not in individual.schedule[i - 1]:
                            fitness -= 90
                        if name not in individual.schedule[i + 1]:
                            fitness -= 90

#            elif i == 1 or i == 28 or i == 55 or i == 82 or i == 109 or i == 125:
#                if name not in individual.schedule[i - 1]:
#                    fitness -= 20

    #Set initial number of scheduled hours to 0
    for tutor in tutors:
        tutorDict[str(tutor) + ": Scheduled"] = 0

    #Add up each tutor's assigned hours
    schedule = individual.schedule
    for shift in schedule:
        for tutor in shift:
            tutorDict[str(tutor) + ": Scheduled"] += 0.5

    #Check if total assigned hours exceeds 19.5
    for tutor in tutors:
        if tutorDict[str(tutor) + ": Scheduled"] > 19.5:
            fitness -= 10 * (tutorDict[str(tutor) + ": Scheduled"] - 19.5)

    #Compare total assigned hours to total requested hours
    for tutor in tutors:
        difference = abs(tutorDict[str(tutor) + ": Scheduled"] - tutorDict[str(tutor) + ": Requested"])
        fitness -= difference**3

    # Check if a preferred shift is assigned
    for i in range(len(individual.schedule)):
        for name in individual.schedule[i]:
            if tutorDict[name][i] == 2:
                fitness += 20

    return fitness

def random_schedule(num_slots, tutors, actualOnDuty):
    schedule = []
    for i in range(num_slots):
        schedule.append(random.sample(tutors, actualOnDuty[i]))

    return schedule

def reproduce(population, pop_size, p_crossover, p_mutation, num_slots, tutors, masterAvailability, actualOnDuty):
    children = []
    for i in range(len(population)):
        parent1 = population[i]
        index = random.randint(0, len(population) - 1)
        while index == i:
            index = random.randint(0, len(population) - 1)
        parent2 = population[index]
        child = crossover(parent1, parent2, p_crossover, num_slots)
        child = mutate(child.schedule, p_mutation, num_slots, tutors, masterAvailability, actualOnDuty)
        children.append(child)
        if len(children) >= pop_size:
            break
    return children

def crossover(parent1, parent2, p_crossover, num_slots):
    if random.random() >= p_crossover:
        offspring = copy.deepcopy(parent1)
        return offspring
    cut = random.randint(1, num_slots - 2)

    schedule = []
    for i in range(num_slots):
        if i < cut:
            schedule.append(parent1.schedule[i])
        else:
            schedule.append(parent2.schedule[i])
    return solution(schedule)

def mutate(schedule, p_mutation, num_slots, tutors, masterAvailability, actualOnDuty):
    new_schedule = []
    for i in range(num_slots):
        staff = []
        if random.random() < p_mutation:
            for tutor in schedule[i]:
                candidate = str(random.sample(masterAvailability[i], 1))
                candidate = candidate[2:-2] # Strip off [' and ']
                # If the candidate is already working, pick another
                while candidate in staff:
                    candidate = str(random.sample(masterAvailability[i], 1))
                    candidate = candidate[2:-2] # Strip off [' and ']
                staff.append(candidate)
        else:
            staff = schedule[i]

        new_schedule.append(staff)

    return solution(new_schedule)

def binary_tournament(population, children, pop_size):
    next_generation = []
    while len(next_generation) < pop_size:
        i, j = random.randint(0, pop_size - 1), random.randint(0, pop_size - 1)
        while j == i:
            j = random.randint(0, pop_size - 1)
        if children[i].fitness >= population[j].fitness:
            next_generation.append(children[i])
        else:
            next_generation.append(population[j])
    return next_generation



#==============================================================================
# Other Functions
#==============================================================================

def makeFig():
    plt.plot(ys, 'ro-')
    return None

class solution:
    def __init__(self, schedule):
        self.schedule = schedule

    def setFitness(self, fitness):
        self.fitness = fitness

    def getFitness(self):
        return self.fitness



#==============================================================================
# Main Function
#==============================================================================

def main(num_slots, pop_size, p_crossover, p_mutation, coinFlip, report, scoreToBeat=-99999):
    os.chdir(availabilityPATH)

    #Get filenames of availability files
    tutors = []
    for filename in os.listdir('.'):
        tutors.append(filename[:-4])

    tutors.sort()

    #Create a tutor name:availability:number of requested hours:number of hours assigned
    #data map for easy reference
    tutorDict = {}
    for tutor in tutors:
        schedule, desired_hours = get_availability(tutor)
        tutorDict[str(tutor)] = schedule
        tutorDict[str(tutor) + ': Requested'] = desired_hours
        tutorDict[str(tutor) + ': Scheduled'] = 0

    # Create a schedule where every time slot contains all available tutors,
    # during that time
    masterAvailability = []
    for i in range(num_slots):
        available = []
        for tutor in tutors:
            if tutorDict[str(tutor)][i] != 0:
                available.append(tutor)
        masterAvailability.append(available)

    # Check to see if there are enough tutors for each time slot, as desired
    actualOnDuty = []
    for i in range(num_slots):
        # If there's fewer tutors available than desired, change desired to how
        # many there are
        if len(masterAvailability[i]) <= onDuty[i]:
            actualOnDuty.append(len(masterAvailability[i]))
        else:
            actualOnDuty.append(onDuty[i])

    # Knowing how many tutors are to be assigned during each time slot, we can
    # calculate the total number of hours that can be assigned
    totalShifts = 0
    for i in range(num_slots):
        totalShifts += actualOnDuty[i]
    totalHoursAvailable = totalShifts / 2

    # Find the total number of requested hours for all tutors
    totalShiftsRequested = 0
    for tutor in tutors:
        for i in range(num_slots):
            if tutorDict[str(tutor)][i] == 1 or tutorDict[str(tutor)][i] == 2: # Incase someone used a 3 or something
                totalShiftsRequested += 1
    totalHoursRequested = totalShiftsRequested / 2

    # Normalize the requested number of hours of each tutor to the number of
    # available hours
    scaleFactor = totalHoursAvailable / totalHoursRequested

    # Adjust each tutor's requested hours to this scale
    for tutor in tutors:
        tutorDict[str(tutor) + ': Original Request'] = tutorDict[str(tutor) + ': Requested'] # save unscaled for later referrence
        tutorDict[str(tutor) + ': Requested'] = scaleFactor * tutorDict[str(tutor) + ': Requested']

    archive = []

    #Generate initial random population
    population = []
    for _ in range(pop_size):
        individual = solution(random_schedule(num_slots, tutors, actualOnDuty))
        population.append(individual)

    #Assign fitness values
    for individual in population:
        fitness = objective(individual, tutorDict, tutors)
        individual.setFitness(fitness)

#    new_pop = []
#    for individual in population:
#        shiftNames = []
#        new_individual = []
#        for i in range(num_slots):
#            tutorsOnDuty = individual.schedule[i]
#            firstNames = []
#            for name in tutorsOnDuty:
#                index = name.index(',')
#                firstName = name[index + 2:]
#                firstNames.append(firstName)
#            shiftNames.append(firstNames)
#        for i in range(len(shiftNames)):
#            shiftNames[i] = sorted(shiftNames[i])
#            new_individual.append(shiftNames[i])
#        new_pop.append(new_individual)
#    archive.append(new_pop)



    #Identify the best solution of the initial population
    best = copy.deepcopy(population[0])
    for individual in population:
        if best.fitness <= individual.fitness:
            best = copy.deepcopy(individual)

    genScores = []
    # Collect data on which generation had which fitness value
    (0, best.fitness)


    #Begin evolving population
    count = -1 # Count the number of consecutive generations without improvement
    iterations = 0 # Count the number of generations
    condition = True # Halting condition to stop new generations
    while condition:
        count += 1

        #Begin population reproduction cycle
        children = reproduce(population, pop_size, p_crossover, p_mutation, num_slots, tutors, masterAvailability, actualOnDuty)

        #Evaluate the offsprings fitnesses
        for child in children:
            fitness = objective(child, tutorDict, tutors)
            child.setFitness(fitness)

        #Identify if an offspring has found a superior solution to the one before
        for child in children:
            if child.fitness > best.fitness:
                best = copy.deepcopy(child)
                count = -1

        #Update graph data
        if report == True:
            ys.append(copy.deepcopy(best.fitness))
            if iterations % 100 == 0:
                print("Generation", iterations, "Score:", round(best.fitness, 2), "count", count)
#                drawnow(makeFig)
#                plt.pause(.0001)

        #Select the next generation population from the previous population and its offsprings
        population = binary_tournament(population, children, pop_size)

#        new_pop = []
#        for individual in population:
#            shiftNames = []
#            new_individual = []
#            for i in range(num_slots):
#                tutorsOnDuty = individual.schedule[i]
#                firstNames = []
#                for name in tutorsOnDuty:
#                    index = name.index(',')
#                    firstName = name[index + 2:]
#                    firstNames.append(firstName)
#                shiftNames.append(firstNames)
#            for i in range(len(shiftNames)):
#                shiftNames[i] = sorted(shiftNames[i])
#                new_individual.append(shiftNames[i])
#            new_pop.append(new_individual)
#        archive.append(new_pop)

        iterations += 1
        genScores.append((iterations, best.fitness))

        if count > 20000:
            condition = False

    # In case of doing multiple consecutive searches, this prevents new results,
    # that are inferior to the current best known, from writing to disk
    if best.fitness > scoreToBeat:
        print("Writing to files")

        #Export schedule
        exportSchedule(best.schedule, actualOnDuty)

        #Export timesheet
        exportPayrollData(best.schedule, tutorDict, tutors)

        #Export important notes about the final schedule
        exportNotes(best.schedule, tutorDict, tutors, dayIndexes)

#        return best.fitness, archive

    return best.fitness, genScores

if __name__ == '__main__':
    num_slots = 132
    populationSize = 5
    crossoverRate = 0.98
    mutationRate = 1/num_slots
    coinFlip = 0.5
    report = True
    scoreToBeat = -99999
#    maxLocalGens = 20

    runs = 1

    start = time.time()
    for _ in range(runs):
        score, archive = main(num_slots, populationSize, crossoverRate, mutationRate, coinFlip, report, scoreToBeat)
        if score > scoreToBeat:
            scoreToBeat = score

#        archivePATH = "\\\\192.168.0.3\\NateFiles\\Science\\Computer Science\\Scheduling Problem\\archive.csv"
#        with open(archivePATH, 'w', newline='\n') as file:
#            genIndex = 0
#            for population in archive:
#                file.write(str(scoreToBeat) + '\n')
#                genLabel = "Generation " + str(genIndex) + '\n'
#                file.write(genLabel)
#                for individual in population:
#                    for i in range(num_slots):
#                        entry = str(individual[i])
#                        entry = entry.replace(',', '')
#                        file.write(entry + ',')
#                    file.write('\n')
#                file.write('\n')
#                genIndex += 1

    print("Best Score:", scoreToBeat)
    print()
    end = time.time()
    duration = end - start
    hours = int(duration // 3600)
    mins = int((duration - hours * 3600) // 60)
    secs = int((duration - hours * 3600 - mins * 60) % 60)

    hours = str(hours)
    mins = str(mins)
    secs = str(secs)

    if len(hours) < 2:
        hours = '0' + hours
    if len(mins) < 2:
        mins = '0' + mins
    if len(secs) < 2:
        secs = '0' + secs

    print("Total elapsed time:", hours + ":" + mins + ":" + secs)
