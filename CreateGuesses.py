import random
import DelineateNetwork
import FileSettings
import numpy as np
import timeit
import re

import time
start_time = time.time()


def readparametersfromfile(constraintfilename=FileSettings.settingsdict['constraintfilename']):
    global percentimpervious, width, slope, impervious_n, pervious_n, impervious_storage, pervious_storage, percent_zero_storage
    constraintfile = open(constraintfilename, 'r')
    for line in constraintfile:
        if (line.find("Percent Impervious") != -1):
            percentimpervious = []
            templine = line.split()
            percentimpervious.append(float(templine[-2]))
            percentimpervious.append(float(templine[-1]))
        elif (line.find("Width") != -1):
            width = []
            templine = line.split()
            width.append(float(templine[-2]))
            width.append(float(templine[-1]))
        elif (line.find("Slope") != -1):
            slope = []
            templine = line.split()
            slope.append(float(templine[-2]))
            slope.append(float(templine[-1]))
        elif (line.find("Impervious N") != -1):
            impervious_n = []
            templine = line.split()
            impervious_n.append(float(templine[-2]))
            impervious_n.append(float(templine[-1]))
        elif (line.find("Pervious N") != -1):
            pervious_n = []
            templine = line.split()
            pervious_n.append(float(templine[-2]))
            pervious_n.append(float(templine[-1]))
        elif (line.find("Impervious Storage") != -1):
            impervious_storage = []
            templine = line.split()
            impervious_storage.append(float(templine[-2]))
            impervious_storage.append(float(templine[-1]))
        elif (line.find("Pervious Storage") != -1):
            pervious_storage = []
            templine = line.split()
            pervious_storage.append(float(templine[-2]))
            pervious_storage.append(float(templine[-1]))
        elif (line.find("Percent Zero Storage") != -1):
            percent_zero_storage = []
            templine = line.split()
            percent_zero_storage.append(float(templine[-2]))
            percent_zero_storage.append(float(templine[-1]))
    return
#readparametersfromfile()


def countsubcatchments(inputfilename=FileSettings.settingsdict['inputfilename']):
    global count
    with open(inputfilename, 'r') as swmmput:
        contents = swmmput.readlines()
        count = len(contents)
    return(count)
#countsubcatchments()


def read_initial_parameters(inputfilename):
    subc_params = []
    subarea_params = []
    global subc_names
    subc_names = []
    subcatchment_parameters = []
    inputfile = open(inputfilename, 'r')
    for line in inputfile:
        if(line.find("[SUBCATCHMENTS]") != -1):
            line = inputfile.readline()
            for i in range(count):
                templine = list(line)
                if templine[0] == ";" or templine[0] == " " or len(templine) < 10:
                    line = inputfile.readline()
                    continue

                elif (line.find("[") != -1):
                    break
                else:
                    linesplit = line.split()
                    subc_params.append(linesplit[4:7])
                    subc_names.append(linesplit[0])
                    line = inputfile.readline()
        if (line.find("[SUBAREAS]") != -1):
            line = inputfile.readline()
            for i in range(count):
                templine = list(line)
                if templine[0] == ";" or templine[0] == " " or len(templine) < 10:
                    line = inputfile.readline()
                    continue
                elif (line.find("[") != -1):
                    break
                else:
                    linesplit = line.split()
                    subarea_params.append(linesplit[1:6])
                    line = inputfile.readline()
    inputfile.close()
    for i in range(len(subc_params)):
        for j in range(len(subarea_params[i])):
            subc_params[i].append(subarea_params[i][j])
        subcatchment_parameters.append(subc_params[i])
    return(subcatchment_parameters)
#read_initial_parameters(FileSettings.settingsdict['inputfilename'])


def read_subc_names(inputfilename):
    subc_params = []
    global subc_names
    subc_names = []
    inputfile = open(inputfilename, 'r')
    for line in inputfile:
        if(line.find("[SUBCATCHMENTS]") != -1):
            line = inputfile.readline()
            for i in range(countsubcatchments(inputfilename)):
                templine = list(line)
                if templine[0] == ";" or templine[0] == " " or len(templine) < 10:
                    line = inputfile.readline()
                    continue

                elif (line.find("[") != -1):
                    break
                else:
                    linesplit = line.split()
                    subc_params.append(linesplit[4:7])
                    subc_names.append(linesplit[0])
                    line = inputfile.readline()
    inputfile.close()
    return subc_names


def transformation_flatten(twoDlistinput):
    oneDlistoutput = []
    for i in range(len(twoDlistinput)):
        for j in range(len(twoDlistinput[i])):
            oneDlistoutput.append(twoDlistinput[i][j])
    return(oneDlistoutput)

def compile_initial_guess(inputfilename):
    global relevant_subcatchment_indices, relevant_subcatchment_parameters, original_guess_flat
    relevant_subcatchment_indices = []
    for allsub in read_subc_names(inputfilename):
        for upstreamsub in DelineateNetwork.list_of_subcatchments:
            if allsub == upstreamsub:
                relevant_subcatchment_indices.append(subc_names.index(allsub))
    relevant_subcatchment_parameters = []
    for i in relevant_subcatchment_indices:
        relevant_subcatchment_parameters.append(read_initial_parameters(inputfilename)[i])
    initial_guess_flat = transformation_flatten(relevant_subcatchment_parameters)
    if inputfilename == FileSettings.settingsdict['distancefilename']:
        original_guess_flat = initial_guess_flat
    return(initial_guess_flat)
#compile_initial_guess(inputfilename)

def caststringsasfloats(inputfilename):
    initial_guess_floats = []
    for guess in compile_initial_guess(inputfilename):
        initial_guess_floats.append(float(guess))
    return(initial_guess_floats)

def caststringsasfloats_distancefile():
    initial_guess_floats = []
    for param in compile_initial_guess(FileSettings.settingsdict["distancefilename"]):
        initial_guess_floats.append(float(param))
    return(initial_guess_floats)

def createrandomsetofP(inputfilename):
    floatnexttemporaryguess = caststringsasfloats(inputfilename)
    for parameter in range(len(floatnexttemporaryguess)):
        binary_setter = random.uniform(0,1)
        if binary_setter > FileSettings.geneticdict['initial_mutation']:
            continue
        else:
            if parameter % 8 == 0:
                floatnexttemporaryguess[parameter] = random.uniform(percentimpervious[0], percentimpervious[1])
            elif parameter % 8 == 1:
                floatnexttemporaryguess[parameter] = random.uniform(width[0], width[1])
            elif parameter % 8 == 2:
                floatnexttemporaryguess[parameter] = random.uniform(slope[0], slope[1])
            elif parameter % 8 == 3:
                floatnexttemporaryguess[parameter] = random.uniform(impervious_n[0], impervious_n[1])
            elif parameter % 8 == 4:
                floatnexttemporaryguess[parameter] = random.uniform(pervious_n[0], pervious_n[1])
            elif parameter % 8 == 5:
                floatnexttemporaryguess[parameter] = random.uniform(impervious_storage[0], impervious_storage[1])
            elif parameter % 8 == 6:
                floatnexttemporaryguess[parameter] = random.uniform(pervious_storage[0], pervious_storage[1])
            elif parameter % 8 == 7:
                floatnexttemporaryguess[parameter] = random.uniform(percent_zero_storage[0], percent_zero_storage[1])
    return(floatnexttemporaryguess)


def crossover(inputfilename, trialfile, survivinglist):
    temporaryguess = compile_initial_guess(inputfilename)
    nexttemporaryguess = compile_initial_guess(random.choice(survivinglist))
    for param in temporaryguess:
        crossover_setter = random.uniform(0,1)
        if crossover_setter > 0.5:
            continue
        else:
            store = param
            nexttemporaryguess[temporaryguess.index(param)] = store
    insertguessestoinputfile(inputfilename, trialfile)
    return(nexttemporaryguess)


def castfloatsasstrings(inputfilename):
    floattostring = createrandomsetofP(inputfilename)
    guess_strings = []
    for float in floattostring:
        guess_strings.append(str(float))
    return(guess_strings)


def transformation_fatten(oneDlistinput):
    new_twoDlistoutput = np.zeros((len(relevant_subcatchment_parameters[0]), len(relevant_subcatchment_parameters)))
    row_count = -1
    col_count = 0
    for oneDparameter in oneDlistinput:
        row_count = row_count + 1
        if row_count < len(relevant_subcatchment_parameters[0]):
            new_twoDlistoutput[row_count][col_count] = oneDparameter
        else:
            row_count = 0
            col_count = col_count + 1
            new_twoDlistoutput[row_count][col_count] = oneDparameter
    return(new_twoDlistoutput)


def insertguessestoinputfile(inputfilename, trialfile):
    guess = transformation_fatten(castfloatsasstrings(inputfilename))

    with open(inputfilename, 'r') as swmmput:
        contents = swmmput.readlines()
        swmmput.seek(0)
        for line in swmmput:
            if line.find('[SUBCATCHMENTS]') != -1:
                for i in range(count):
                    line = swmmput.readline()
                    linelist = list(line)
                    if linelist[0] == " " or linelist[0] == ";" or len(linelist) < 10:
                        continue
                    elif (line.find('[SUBAREAS]') != -1):
                        break
                    else:
                        for sub in DelineateNetwork.list_of_subcatchments:
                            templine = contents.index(line)
                            splitline = contents[templine].split()
                            if splitline[0] == sub:
                                splitline[4] = str(guess[0][DelineateNetwork.list_of_subcatchments.index(sub)])
                                splitline[5] = str(guess[1][DelineateNetwork.list_of_subcatchments.index(sub)])
                                splitline[6] = str(guess[2][DelineateNetwork.list_of_subcatchments.index(sub)])
                                contents[templine] = "      ".join(splitline) + "\n"
                                break
            if line.find('[SUBAREAS]') != -1:
                for i in range(count):
                    line = swmmput.readline()
                    linelist = list(line)
                    if linelist[0] == " " or linelist[0] == ";" or len(linelist) < 10:
                        continue
                    elif (line.find('[') != -1):
                        break
                    else:
                        for sub in DelineateNetwork.list_of_subcatchments:
                            templine = contents.index(line)
                            splitline = contents[templine].split()
                            if splitline[0] == sub:
                                splitline[1] = str(guess[3][DelineateNetwork.list_of_subcatchments.index(sub)])
                                splitline[2] = str(guess[4][DelineateNetwork.list_of_subcatchments.index(sub)])
                                splitline[3] = str(guess[5][DelineateNetwork.list_of_subcatchments.index(sub)])
                                splitline[4] = str(guess[6][DelineateNetwork.list_of_subcatchments.index(sub)])
                                splitline[5] = str(guess[7][DelineateNetwork.list_of_subcatchments.index(sub)])
                                contents[templine] = "      ".join(splitline) + '\n'
                                break
    print("Time for everything else:", time.time() - start_time)
    with open(trialfile, 'w') as newfile:
        for i in range(count):
            newfile.write(contents[i])
    newfile.close()
    print("Time for writing:", time.time() - start_time)
    return

def create_generation(inputfilename, filelist):
    for trialfile in filelist:
        insertguessestoinputfile(inputfilename, trialfile)
    return
#create_generation(FileSettings.settingsdict['inputfilename'], FileSettings.settingsdict['filelist'])

#print(timeit.timeit(stmt= mycode, number=1000))
