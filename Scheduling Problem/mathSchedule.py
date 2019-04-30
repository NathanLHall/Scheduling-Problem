# -*- coding: utf-8 -*-
"""
Created on Sat Dec 15 04:17:06 2018

@author: NathanLHall
"""

import copy
import csv
from drawnow import *
import matplotlib.pyplot as plt
import os
import random
import time

# =============================================================================
# Shelby Variables
# =============================================================================

# Shelby, you can make changes to these variables, as you see fit

#Folder location to find tutor availability schedules
#availabilityPATH = "\\\\192.168.0.3\\NateFiles\\Science\\Computer Science\\Scheduling Problem\\Tutor Availabilities\\"
#templatePATH = "\\\\192.168.0.3\\NateFiles\\Science\\Computer Science\\Scheduling Problem\\Template.csv"
#payrollPATH = "\\\\192.168.0.3\\NateFiles\\Science\\Computer Science\\Scheduling Problem\\Weekly Payroll.csv"
#mathSchedulePATH = "\\\\192.168.0.3\\NateFiles\\Science\\Computer Science\\Scheduling Problem\\Weekly Schedule.csv"
#notesPATH = "\\\\192.168.0.3\\NateFiles\\Science\\Computer Science\\Scheduling Problem\\Notes.txt"

# Running from Ubuntu
availabilityPATH = "/run/user/1000/gvfs/smb-share:server=192.168.0.3,share=natefiles/Science/Computer Science/Scheduling Problem/Tutor Availabilities/"
templatePATH = "/run/user/1000/gvfs/smb-share:server=192.168.0.3,share=natefiles/Science/Computer Science/Scheduling Problem/Template.csv"
payrollPATH = "/run/user/1000/gvfs/smb-share:server=192.168.0.3,share=natefiles/Science/Computer Science/Scheduling Problem/Weekly Payroll.csv"
mathSchedulePATH = "/run/user/1000/gvfs/smb-share:server=192.168.0.3,share=natefiles/Science/Computer Science/Scheduling Problem/Weekly Schedule.csv"
notesPATH = "/run/user/1000/gvfs/smb-share:server=192.168.0.3,share=natefiles/Science/Computer Science/Scheduling Problem/Notes.txt"

# =============================================================================
# Not Shelby Variables
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

#Number of tutors on duty
numTutors = 3

# =============================================================================
# GA Function Definitions
# =============================================================================
def objective(individual, tutorDict, tutors):
    fitness = 0

    #Check for shift assignments during unavailable times
    for i in range(len(individual.schedule)):
        for name in individual.schedule[i]:
            if tutorDict[name][i] == 0:
                fitness -= 10

            #Check for shift assignments that are less than 1 hour long
            if i == 0:
                if name not in individual.schedule[i + 1]:
                    fitness -= 1
            if i > 0 and i < len(individual.schedule) - 2:
                if name not in individual.schedule[i - 1] and name not in individual.schedule[i + 1]:
                    fitness -= 1

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
        fitness -= 0.5 * difference

    return fitness

def crossover(parent1, parent2, p_crossover, num_bits):
    if random.random() >= p_crossover:
        offspring = copy.deepcopy(parent1)
        return offspring
    cut = random.randint(1, num_bits - 2)

    schedule = []
    for i in range(num_bits):
        if i < cut:
            schedule.append(parent1.schedule[i])
        else:
            schedule.append(parent2.schedule[i])
    return solution(schedule)

#Converts a constant mutation rate into a variable rate
#Iterable is anything that will change over time (ex. generation count)
#Direction is either postive or negative one (-1 or 1)
#Needs further work, as there are MANY ways of doing this
def mutate(schedule, p_mutation, num_bits, tutors):
    new_schedule = []
    for i in range(num_bits):
        if random.random() < p_mutation:
            #Replace all 3 tutors from the given shift
            staff = random.sample(tutors, 3)
        else:
            staff = schedule[i]
        new_schedule.append(staff)
    return solution(new_schedule)

def reproduce(population, pop_size, p_crossover, p_mutation, num_bits, tutors):
    children = []
    for parent1 in population:
        parent2 = random.choice(population)
        while parent2 == parent1:
            parent2 = random.choice(population)
        child = crossover(parent1, parent2, p_crossover, num_bits)
        child = mutate(child.schedule, p_mutation, num_bits, tutors)
        children.append(child)
        if len(children) >= pop_size:
            break
    return children

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

    schedule =[]
    for i in range(6):
        for j in range(27):
            if contents[j][i] != '':
                schedule.append(int(contents[j][i]))

    tutorDict[filename] = schedule

    return schedule, desired_hours

def random_schedule(num_bits, tutors):
    schedule = []
    for i in range(num_bits):
        schedule.append(random.sample(tutors, 3))

    return schedule

def createSlotEntry(index, day, shiftNames):
    entry = ''
    for i in range(numTutors):
        entry += shiftNames[day + index][i]
        if i < numTutors - 1:
            entry += ' '
        else:
            entry += ','
    return entry

def createRow(index, shiftNames):
    entries = ''
    for day in dayIndexes:
        if index in range(offset, offset + sat_slots):
            if day != satIndex:
                entry = createSlotEntry(index, day, shiftNames)
            else:
                entry = createSlotEntry(index - 5, day, shiftNames)
        elif index in range(offset) or index in range(offset + sat_slots, fri_slots):
            if day != satIndex:
                entry = createSlotEntry(index, day, shiftNames)
            else:
                continue
        else:
            if day < friIndex:
                entry = createSlotEntry(index, day, shiftNames)
            else:
                continue

        entries += entry
    entries += '\n'
    return entries

def exportSchedule(schedule):
    shiftNames = []
    for i in range(len(schedule)):
        onDuty = schedule[i]
        firstNames = []
        for name in onDuty:
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
            row_contents = createRow(i, shiftNames)
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
        count = 0
        fixes = []
        for i in range(len(schedule)):
            AMPM = "AM"
            if tutorDict[str(tutor)][i] == 0 and tutor in schedule[i]:
                count += 1
                for j in range(len(dayIndexes)):
                    if i in range(dayIndexes[j]):
                        day = days[j]
                        slot = i - dayIndexes[j] + 27
                        hour = int(7 + slot // 2 + slot % 2)
                        if hour > 12:
                            hour = hour % 12
                            AMPM = "PM"
                        minute = int((slot % 2) * 30)
                        fixes.append(str(day) + " - " + str(hour) + ":" + str(minute) + " " + AMPM)
        if len(fixes) == 0:
            notes.append(str(tutor) + ":" +
             "\n\tRequested Hours: " + str(tutorDict[str(tutor) + ": Requested"]) +
             "\n\tScheduled Hours: " + str(tutorDict[str(tutor) + ": Scheduled"]) +
             "\n\tDifference: " + str(tutorDict[str(tutor) + ": Scheduled"] - (tutorDict[str(tutor) + ": Requested"])) + " hrs\n\n")

        if len(fixes) > 0:
            notes.append(str(tutor) + ":" +
                "\n\tRequested Hours: " + str(tutorDict[str(tutor) + ": Requested"]) +
                "\n\tScheduled Hours: " + str(tutorDict[str(tutor) + ": Scheduled"]) +
                "\n\tDifference: " + str(tutorDict[str(tutor) + ": Scheduled"] - (tutorDict[str(tutor) + ": Requested"])) + " hrs" +
                "\n\t" + str(len(fixes)) + " schedule conflicts:")
            for i in range(len(fixes)):
                notes.append("\n\t\t" + fixes[i])
            notes.append("\n\n")

    with open(notesPATH, 'w') as file:
        for i in range(len(notes)):
            file.write(notes[i])

    return None

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

def main(max_gens, num_bits, pop_size, p_crossover, p_mutation, coinFlip, max_local_gens):
    os.chdir(availabilityPATH)

    #Get filenames of availability files
    tutors = []
    for filename in os.listdir('.'):
        tutors.append(filename[:-4])

    #Create a tutor name:availability:number of requested hours:number of hours assigned
    #data map for easy reference
    tutorDict = {}
    for tutor in tutors:
        schedule, desired_hours = get_availability(tutor)
        tutorDict[str(tutor)] = schedule
        tutorDict[str(tutor) + ': Requested'] = desired_hours
        tutorDict[str(tutor) + ': Scheduled'] = 0

    #Generate initial random population
    population = []
    for _ in range(pop_size):
        individual = solution(random_schedule(num_bits, tutors))
        population.append(individual)

    #Assign fitness values
    for individual in population:
        fitness = objective(individual, tutorDict, tutors)
        individual.setFitness(fitness)

    #Identify the best solution of the initial population
    best = copy.deepcopy(population[0])
    for individual in population:
        if best.fitness <= individual.fitness:
            best = copy.deepcopy(individual)

    #Store the best fitness value of starting population, and add it to the graphing dataset
    ys.append(copy.deepcopy(best.fitness))

    #Begin evolving population
    for i in range(max_gens):

        #Begin population reproduction cycle
        children = reproduce(population, pop_size, p_crossover, p_mutation, num_bits, tutors)

        #Evaluate the offsprings fitnesses
        for child in children:
            fitness = objective(child, tutorDict, tutors)
            child.setFitness(fitness)

        #Identify if an offspring has found a superior solution to the one before
        for child in children:
            if child.fitness >= best.fitness:
                best = copy.deepcopy(child)

        #Update graph data
        ys.append(copy.deepcopy(best.fitness))
        if i % 100 == 0:
            print(str(int(round(i/max_gens, 2) * 100)) + "% Complete")
            print("Current Best Score:", best.fitness)
            print("Fitness Performance (Generations 0 to " + str(i) + "):")
            drawnow(makeFig)
            print("----------------------------------------")
            print()
        plt.pause(.0001)

        #Select the next generation population from the previous population and its offsprings
        population = binary_tournament(population, children, pop_size)


    #Export schedule
    exportSchedule(best.schedule)

    #Export timesheet
    exportPayrollData(best.schedule, tutorDict, tutors)

    #Export important notes about the final schedule
    exportNotes(best.schedule, tutorDict, tutors, dayIndexes)

    return best.fitness

if __name__ == '__main__':
    crossoverRate = 0.98
    coinFlip = 0.5
    maxGens = 2000
    maxLocalGens = 20
    mutationRate = 1.0/132
    num_bits = 132
    populationSize = 100

    start = time.time()
    score = main(maxGens, num_bits, populationSize, crossoverRate, mutationRate, coinFlip, maxLocalGens)
    print("Final Fitness Score:", score)
    print()
    end = time.time()
    duration = end - start
    hours = int(duration // 3600)
    mins = int((duration - hours * 3600) // 60)
    secs = int((duration - hours * 3600 - mins * 60) % 60)
    print("Total elapsed time:", str(hours) + ":" + str(mins) + ":" + str(secs))