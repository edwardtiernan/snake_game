import random
import DelineateNetwork
import numpy as np
import FileSettings
import CreateGuesses
import Objective_functions
import Generations


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
            for i in range(CreateGuesses.count):
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
            for i in range(CreateGuesses.count):
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
#read_initial_parameters(inputfilename)


def transformation_flatten(twoDlistinput):
    oneDlistoutput = []
    for i in range(len(twoDlistinput)):
        for j in range(len(twoDlistinput[i])):
            oneDlistoutput.append(twoDlistinput[i][j])
    return(oneDlistoutput)


def compile_initial_guess(inputfilename):
    global relevant_subcatchment_indices, relevant_subcatchment_parameters
    relevant_subcatchment_indices = []
    for allsub in CreateGuesses.subc_names:
        for upstreamsub in DelineateNetwork.list_of_subcatchments:
            if allsub == upstreamsub:
                relevant_subcatchment_indices.append(CreateGuesses.subc_names.index(allsub))
    relevant_subcatchment_parameters = []
    for i in relevant_subcatchment_indices:
        relevant_subcatchment_parameters.append(read_initial_parameters(inputfilename)[i])
    initial_guess_flat = transformation_flatten(relevant_subcatchment_parameters)
    return(initial_guess_flat)
#compile_initial_guess(inputfilename)


def caststringsasfloats(parameterlist):
    initial_guess_floats = []
    for guess in parameterlist:
        initial_guess_floats.append(float(guess))
    return(initial_guess_floats)

def createrandomsetofP(survivinglist):
    floatnexttemporaryguess = caststringsasfloats(crossover(survivinglist))
    for parameter in range(len(floatnexttemporaryguess)):
        binary_setter = random.uniform(0,1)
        if binary_setter > 0.1:
            continue
        else:
            if parameter % 8 == 0:
                floatnexttemporaryguess[parameter] = random.uniform(CreateGuesses.percentimpervious[0], CreateGuesses.percentimpervious[1])
            elif parameter % 8 == 1:
                floatnexttemporaryguess[parameter] = random.uniform(CreateGuesses.width[0], CreateGuesses.width[1])
            elif parameter % 8 == 2:
                floatnexttemporaryguess[parameter] = random.uniform(CreateGuesses.slope[0], CreateGuesses.slope[1])
            elif parameter % 8 == 3:
                floatnexttemporaryguess[parameter] = random.uniform(CreateGuesses.impervious_n[0], CreateGuesses.impervious_n[1])
            elif parameter % 8 == 4:
                floatnexttemporaryguess[parameter] = random.uniform(CreateGuesses.pervious_n[0], CreateGuesses.pervious_n[1])
            elif parameter % 8 == 5:
                floatnexttemporaryguess[parameter] = random.uniform(CreateGuesses.impervious_storage[0], CreateGuesses.impervious_storage[1])
            elif parameter % 8 == 6:
                floatnexttemporaryguess[parameter] = random.uniform(CreateGuesses.pervious_storage[0], CreateGuesses.pervious_storage[1])
            elif parameter % 8 == 7:
                floatnexttemporaryguess[parameter] = random.uniform(CreateGuesses.percent_zero_storage[0], CreateGuesses.percent_zero_storage[1])
    return(floatnexttemporaryguess)


def fillmatingpool(survivinglist):
    matingpool =[]
    dummylist = [x for x in survivinglist]
    for i in range(FileSettings.geneticdict['population']+10):
        choice1 = random.choice(dummylist)
        choice2 = random.choice(dummylist)
        while choice2 == choice1:
            choice2 = random.choice(dummylist)
        if Objective_functions.par_aggFunc[survivinglist.index(choice1)] < \
                Objective_functions.par_aggFunc[survivinglist.index(choice2)]:
            matingpool.append(choice1)
            dummylist.remove(choice1)
        else:
            matingpool.append(choice2)
            dummylist.remove(choice2)

    global not_selected_list
    not_selected_list = dummylist
    return(matingpool)


def crossover(survivinglist):
    choice1 = random.choice(survivinglist)
    survivinglist.remove(choice1)
    choice2 = random.choice(survivinglist)
    #while choice2 == choice1:
        #choice2 = random.choice()
    choices = [choice1, choice2]
    Objective_functions.readobservationfile(FileSettings.settingsdict['observationdatafile'])
    Objective_functions.objectivefunctions(choices, FileSettings.settingsdict['observationdatafile'],
                                           FileSettings.settingsdict['distancefilename'],
                                           FileSettings.settingsdict['root'])
    guesses_Agg = Objective_functions.aggregateFunction()
    betterguess = choices[guesses_Agg.index(min(guesses_Agg))]
    worserguess = choices[guesses_Agg.index(max(guesses_Agg))]
    bettertemporaryguess = compile_initial_guess(betterguess)
    worsertemporaryguess = compile_initial_guess(worserguess)
    threshhold = random.uniform(0, FileSettings.geneticdict['crossover_bias'])
    for param in bettertemporaryguess:
        crossover_setter = random.uniform(0, 1)
        if crossover_setter > (threshhold + FileSettings.geneticdict['crossover_bias']):
            continue
        else:
            store = param
            worsertemporaryguess[bettertemporaryguess.index(param)] = store
    return(worsertemporaryguess)


def castfloatsasstrings(survivinglist):
    floattostring = createrandomsetofP(survivinglist)
    guess_strings = []
    for float in floattostring:
        guess_strings.append(str(float))
    return(guess_strings)

def transformation_fatten(oneDlistinput):
    new_twoDlistoutput = np.zeros((len(relevant_subcatchment_parameters[0]),len(relevant_subcatchment_parameters)))
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

def insertguessestoinputfile(inputfilename, trialfile, survivinglist):
    guess = transformation_fatten(castfloatsasstrings(survivinglist))

    with open(inputfilename, 'r') as swmmput:
        contents = swmmput.readlines()
        swmmput.seek(0)
        for line in swmmput:
            if line.find('[SUBCATCHMENTS]') != -1:
                for i in range(CreateGuesses.count):
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
                for i in range(CreateGuesses.count):
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
    with open(trialfile, 'w') as newfile:
        for i in range(CreateGuesses.count):
            newfile.write(contents[i])
    newfile.close()
    return


def create_next_generation(inputfilename, filelist, survivinglist):
    for trialfile in filelist:
        insertguessestoinputfile(inputfilename, trialfile, survivinglist)
    return

