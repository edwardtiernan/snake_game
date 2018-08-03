"""Import
FileSettings to access SWMMCALPY Decision Variables
DelineateNetwork for 'list_of_subcatchments' - list of strings containing subcatchments upstream from root
Main to call the initialized pool.map() function
Numpy to gain access to the array data structure.  Allows us to get away from 2D lists
Random to generate random numbers from a uniform distribution
Multiprocessing to access pool functions for inputfile creation
Time to access tools for speedup analysis
"""
import FileSettings
import DelineateNetwork
import ObjectiveFunctions
import Main
import Generations
import numpy as np
import random
import multiprocessing
import time


def readparametersfromfile(constraintfilename=FileSettings.settingsdict['constraintfilename']):
    """

    :param constraintfilename: Parameter_ranges.txt that contains the keyword - value (low high) for each surface
                                parameter in SWMM
    :return: initialized lists (len == 2) containing the bounds for the feasible parameter space.  The allowable
            paramters are preset.  This could potentially be improved by using an array where the number of rows is
            the number of parameter types, and the 2 columns are the low and high values.  The list of parameter types
            would have to match exactly the strings used in the input files.
    """
    global percentimpervious, width, slope, impervious_n, pervious_n, impervious_storage, pervious_storage, \
        percent_zero_storage
    constraintfile = open(constraintfilename, 'r')
    for line in constraintfile:
        if line.find("Percent Impervious") != -1:
            percentimpervious = []
            templine = line.split()
            percentimpervious.append(float(templine[-2]))
            percentimpervious.append(float(templine[-1]))
        elif line.find("Width") != -1:
            width = []
            templine = line.split()
            width.append(float(templine[-2]))
            width.append(float(templine[-1]))
        elif line.find("Slope") != -1:
            slope = []
            templine = line.split()
            slope.append(float(templine[-2]))
            slope.append(float(templine[-1]))
        elif line.find("Impervious N") != -1:
            impervious_n = []
            templine = line.split()
            impervious_n.append(float(templine[-2]))
            impervious_n.append(float(templine[-1]))
        elif line.find("Pervious N") != -1:
            pervious_n = []
            templine = line.split()
            pervious_n.append(float(templine[-2]))
            pervious_n.append(float(templine[-1]))
        elif line.find("Impervious Storage") != -1:
            impervious_storage = []
            templine = line.split()
            impervious_storage.append(float(templine[-2]))
            impervious_storage.append(float(templine[-1]))
        elif line.find("Pervious Storage") != -1:
            pervious_storage = []
            templine = line.split()
            pervious_storage.append(float(templine[-2]))
            pervious_storage.append(float(templine[-1]))
        elif line.find("Percent Zero Storage") != -1:
            percent_zero_storage = []
            templine = line.split()
            percent_zero_storage.append(float(templine[-2]))
            percent_zero_storage.append(float(templine[-1]))
    return


readparametersfromfile()


def count_contents(inputfilename=FileSettings.settingsdict['inputfilename']):
    """
    :param inputfilename:
    :return: defines globals "count" - the length of the input file
                            "contents" - the string of each line in the input file
    """
    global count, contents
    with open(inputfilename, 'r') as swmmput:
        contents = swmmput.readlines()
        count = len(contents)
    return count


count_contents()


def read_initial_parameters(inputfilename):
    """Opens the input file and reads the parameters in the [SUBCATCHMENT] and [SUBAREA] headers.  These values
    are initially put in separate 2D lists, but are then added as floats to the initial numpy array.
    :param inputfilename:
    :return: "np_subcatchment_parameters" - numpy array where the rows are each subcatchment in the input file
                                            (even the extraneous ones) and the columns are each surface parameter type.
    """
    subc_params = []
    subarea_params = []
    global subc_names
    subc_names = []
    # I'm keeping the manual parser as an open-read-close workflow because I think I need to call this function
    #   for each input file in each generation.  But it would be nice to get away from that.
    inputfile = open(inputfilename, 'r')
    for line in inputfile:
        if line.find("[SUBCATCHMENTS]") != -1:
            line = inputfile.readline()
            for i in range(count):
                templine = list(line)
                if templine[0] == ";" or templine[0] == " " or len(templine) < 10:
                    line = inputfile.readline()
                    continue

                elif line.find("[") != -1:
                    break
                else:
                    linesplit = line.split()
                    subc_params.append(linesplit[4:7])
                    subc_names.append(linesplit[0])
                    line = inputfile.readline()
        if line.find("[SUBAREAS]") != -1:
            line = inputfile.readline()
            for i in range(count):
                templine = list(line)
                if templine[0] == ";" or templine[0] == " " or len(templine) < 10:
                    line = inputfile.readline()
                    continue
                elif line.find("[") != -1:
                    break
                else:
                    linesplit = line.split()
                    subarea_params.append(linesplit[1:6])
                    line = inputfile.readline()
    inputfile.close()

    # Initialize the numpy array and add the float(values) to it
    global np_subcatchment_parameters
    np_subcatchment_parameters = np.empty((len(subc_params), len(subc_params[0]) + len(subarea_params[0])), dtype=float)
    for row in range(len(subc_params)):
        for col in range(len(subc_params[0])):
            np_subcatchment_parameters[row, col] = float(subc_params[row][col])
    for row in range(len(subarea_params)):
        for col in range(len(subarea_params[0])):
            np_subcatchment_parameters[row, col + len(subc_params[0])] = float(subarea_params[row][col])
    return np_subcatchment_parameters


def compile_initial_guess(inputfilename):
    """ Determines which rows in the "np_subcatchment_parameters" array match the
    "DelineateNetwork.list_of_subcatchments" list.  "np_subcatchment_parameters" is then masked to form a new array
    with <= number of rows called "np_initial_guess".  This "np_initial_guess" array is the array that receives mutation
    operations and gets reapplied to the input files.
    :param inputfilename: This function needs to read an input file in order to produce the array that will be
                        mutated.
    :return: "np_initial_guess" - masked array from "np_subcatchment_parameters".  All columns are maintained but the
            number of rows may be reduced to only those corresponding to subcatchments upstream of the root.
    """
    global relevant_subcatchment_indices, np_initial_guess
    relevant_subcatchment_indices = []
    read_initial_parameters(inputfilename)
    for allsub in subc_names:
        for upstreamsub in DelineateNetwork.list_of_subcatchments:
            if allsub == upstreamsub:
                relevant_subcatchment_indices.append(subc_names.index(allsub))

    # This line creates an array where each relevant subcatchment is a row and each parameter type is a column.
    np_initial_guess = np_subcatchment_parameters[relevant_subcatchment_indices]
    return np_initial_guess

global inputfile_initial_guess
inputfile_initial_guess = compile_initial_guess(FileSettings.settingsdict['inputfilename'])


def np_createrandomset():
    """Creates a copy of the "np_initial_guess" array and subjects that copy to the mutation criteria for producing the
    first generation of guesses from the starting point input file.

    :param: De facto input is the starting inputfilename.  This function is not given a formal argument
                        because more than 1 argument messes with the parallelization.  This will have to be different
                        for subsequent generations.
    :return: "np_new_guess" - copy of the "np_initial_guess" where some of the parameters have been mutated according to
                            their specific surface parameter type's uniform distribution.
    """

    np_new_guess = np.copy(inputfile_initial_guess)
    for row in range(len(np_new_guess)):
        for col in range(len(np_new_guess[0])):
            binary_setter = random.uniform(0, 1)
            if binary_setter > FileSettings.geneticdict['initial_mutation']:
                continue
            else:
                if col == 0:
                    np_new_guess[row, col] = random.uniform(percentimpervious[0], percentimpervious[1])
                elif col == 1:
                    np_new_guess[row, col] = random.uniform(width[0], width[1])
                elif col == 2:
                    np_new_guess[row, col] = random.uniform(slope[0], slope[1])
                elif col == 3:
                    np_new_guess[row, col] = random.uniform(impervious_n[0], impervious_n[1])
                elif col == 4:
                    np_new_guess[row, col] = random.uniform(pervious_n[0], pervious_n[1])
                elif col == 5:
                    np_new_guess[row, col] = random.uniform(impervious_storage[0], impervious_storage[1])
                elif col == 6:
                    np_new_guess[row, col] = random.uniform(pervious_storage[0], pervious_storage[1])
                elif col == 7:
                    np_new_guess[row, col] = random.uniform(percent_zero_storage[0], percent_zero_storage[1])
    return np_new_guess


def insertguessestoinputfile(trialfile):
    """Calls np_createrandomset() to grab the mutated "np_new_guess".  The "contents" list of strings is then revisted.
    Where the [SUBCATCHMENTS] and [SUBAREAS] headers are found, the string is split and the parameter values are
    replaced with those from the "np_new_guess" array.  Then the entire amended "contents" list is printed back into a
    newly created "trialfileXX.inp".  This function is called in parallel.

    :param trialfile:
    :return: The end result is an input file containing the mutated parameter values contained within "np_new_guess"
    """
    start_time = time.time()

    guess = np_createrandomset()
    subcatchment_index = contents.index('[SUBCATCHMENTS]\n')
    subareas_index = contents.index('[SUBAREAS]\n')
    for line in contents[subcatchment_index+1:]:
        linelist = list(line)
        if linelist[0] == " " or linelist[0] == ";" or len(linelist) < 10:
            continue
        elif line.find('[') != -1:
            break
        else:
            for sub in DelineateNetwork.list_of_subcatchments:
                templine = contents.index(line)
                splitline = contents[templine].split()
                if splitline[0] == sub:
                    splitline[4] = str(guess[DelineateNetwork.list_of_subcatchments.index(sub)][0])
                    splitline[5] = str(guess[DelineateNetwork.list_of_subcatchments.index(sub)][1])
                    splitline[6] = str(guess[DelineateNetwork.list_of_subcatchments.index(sub)][2])
                    contents[templine] = "      ".join(splitline) + "\n"
                    break

    for line in contents[subareas_index+1:]:
        linelist = list(line)
        if linelist[0] == " " or linelist[0] == ";" or len(linelist) < 10:
            continue
        elif line.find('[') != -1:
            break
        else:
            for sub in DelineateNetwork.list_of_subcatchments:
                templine = contents.index(line)
                splitline = contents[templine].split()
                if splitline[0] == sub:
                    splitline[1] = str(guess[DelineateNetwork.list_of_subcatchments.index(sub)][3])
                    splitline[2] = str(guess[DelineateNetwork.list_of_subcatchments.index(sub)][4])
                    splitline[3] = str(guess[DelineateNetwork.list_of_subcatchments.index(sub)][5])
                    splitline[4] = str(guess[DelineateNetwork.list_of_subcatchments.index(sub)][6])
                    splitline[5] = str(guess[DelineateNetwork.list_of_subcatchments.index(sub)][7])
                    contents[templine] = "      ".join(splitline) + '\n'
                    break
    with open(trialfile, 'w') as newfile:
        for i in range(count):
            newfile.write(contents[i])
    newfile.close()
    print("Time for file creation: ", time.time() - start_time)
    return


def par_creategenerations():
    """ This function controls the parallelized construction of the initial 200 input files.  It inherets the "pool"
    variable from the pool_initializer() function in Main.py.  This allows for the same multiprocessing variable to be
    used for several applications within SWMMCALPY, avoiding the reallocation of processes which caused it to blow up.

    :return:
    """
    pool = Main.pool_initializer()
    pool.map(insertguessestoinputfile, FileSettings.settingsdict['Unionsetlist'])
    return


def next_fillmatingpool(survivinglist=FileSettings.settingsdict['Unionsetlist']):
    """This function implements the tournament selection for persisting guesses within the aggregate function
    methodology. It evaluates two random input files from the previous generation, and adds the better one to the
    "matingpool" list.  If an input file is added, it is removed from the tournament pool, "dummylist".  Right now,
    of the 200 input files in each generation, 110 make it into "matingpool".

    :param survivinglist: exhaustive list of all input files
    :return matingpool: list of only the input file names that have passed the tournament selection
    """
    global matingpool
    matingpool = []
    dummylist = [x for x in survivinglist]
    for i in range(FileSettings.geneticdict['population']+25):
        choice1 = random.choice(dummylist)
        choice2 = random.choice(dummylist)
        while choice2 == choice1:
            choice2 = random.choice(dummylist)
        if ObjectiveFunctions.par_aggFunc[survivinglist.index(choice1)] < \
                ObjectiveFunctions.par_aggFunc[survivinglist.index(choice2)]:
            matingpool.append(choice1)
            dummylist.remove(choice1)
        else:
            matingpool.append(choice2)
            dummylist.remove(choice2)

    global not_selected_list
    not_selected_list = dummylist
    return


def next_crossover():
    """This function implements the crossover portion of the mutations required by NSGA-II. On the heels of the global
    "matingpool" list being created, next_crossover() chooses 2 of those input files, determines which one is superior,
    and preferentially overwrites the "worseguess" input file with the superior parameters from the "betterguess".
    This ensures that the superior guess's genetic information propogates, but maintains some diversity from the
    inferior guess's parameters values.

    De facto paramater matingpool: list created by next_fillmatingpool
    :return worsetemporaryguess: numpy array containing the mutated guess to be put back into the input file
    """
    choice1 = matingpool[0]
    matingpool.remove(choice1)
    choice2 = random.choice(matingpool)
    choices = [choice1, choice2]
    ObjectiveFunctions.objectivefunctions(choices, FileSettings.settingsdict['observationdatafile'],
                                          FileSettings.settingsdict['distancefilename'],
                                          FileSettings.settingsdict['root'])
    guesses_Agg = ObjectiveFunctions.aggregateFunction()
    betterguess = choices[guesses_Agg.index(min(guesses_Agg))]
    worseguess = choices[guesses_Agg.index(max(guesses_Agg))]
    bettertemporaryguess = compile_initial_guess(betterguess)
    worsetemporaryguess = compile_initial_guess(worseguess)
    threshhold = random.uniform(0, FileSettings.geneticdict['crossover_bias'])
    for i in range(len(bettertemporaryguess)):
        for j in range(len(bettertemporaryguess[0])):
            crossover_setter = random.uniform(0, 1)
            if crossover_setter > (threshhold + FileSettings.geneticdict['crossover_bias']):
                continue
            else:
                store = bettertemporaryguess[i][j]
                worsetemporaryguess[i][j] = store
    return worsetemporaryguess


def next_np_createrandomset(matingpool_array):
    """Creates a copy of the "np_initial_guess" array and subjects that copy to the mutation criteria for producing the
    first generation of guesses from the starting point input file.

    :param: De facto input is the mutated numpy array from the worse guess in the next_crossover function.
    :return np_new_guess: further mutated numpy array to be reinserted into the "contents" list and reconstructed into
                            an input file.
    """
    np_new_guess = matingpool_array
    for row in range(len(np_new_guess)):
        for col in range(len(np_new_guess[0])):
            binary_setter = random.uniform(0, 1)
            if binary_setter > FileSettings.geneticdict['nsga_mutation']:
                continue
            else:
                if col == 0:
                    np_new_guess[row, col] = random.uniform(percentimpervious[0], percentimpervious[1])
                elif col == 1:
                    np_new_guess[row, col] = random.uniform(width[0], width[1])
                elif col == 2:
                    np_new_guess[row, col] = random.uniform(slope[0], slope[1])
                elif col == 3:
                    np_new_guess[row, col] = random.uniform(impervious_n[0], impervious_n[1])
                elif col == 4:
                    np_new_guess[row, col] = random.uniform(pervious_n[0], pervious_n[1])
                elif col == 5:
                    np_new_guess[row, col] = random.uniform(impervious_storage[0], impervious_storage[1])
                elif col == 6:
                    np_new_guess[row, col] = random.uniform(pervious_storage[0], pervious_storage[1])
                elif col == 7:
                    np_new_guess[row, col] = random.uniform(percent_zero_storage[0], percent_zero_storage[1])
    return np_new_guess


def next_insertguessestoinputfile(matingpool_array, trialfile):
    """Calls np_createrandomset() to grab the mutated "np_new_guess".  The "contents" list of strings is then revisted.
    Where the [SUBCATCHMENTS] and [SUBAREAS] headers are found, the string is split and the parameter values are
    replaced with those from the "np_new_guess" array.  Then the entire amended "contents" list is printed back into a
    newly created "trialfileXX.inp".  This function is called in parallel.

    :param trialfile:
    :return: The end result is an input file containing the mutated parameter values contained within "np_new_guess"
    """
    guess = next_np_createrandomset(matingpool_array)
    subcatchment_index = contents.index('[SUBCATCHMENTS]\n')
    subareas_index = contents.index('[SUBAREAS]\n')
    for line in contents[subcatchment_index+1:]:
        linelist = list(line)
        if linelist[0] == " " or linelist[0] == ";" or len(linelist) < 10:
            continue
        elif line.find('[') != -1:
            break
        else:
            for sub in DelineateNetwork.list_of_subcatchments:
                templine = contents.index(line)
                splitline = contents[templine].split()
                if splitline[0] == sub:
                    splitline[4] = str(guess[DelineateNetwork.list_of_subcatchments.index(sub)][0])
                    splitline[5] = str(guess[DelineateNetwork.list_of_subcatchments.index(sub)][1])
                    splitline[6] = str(guess[DelineateNetwork.list_of_subcatchments.index(sub)][2])
                    contents[templine] = "      ".join(splitline) + "\n"
                    break

    for line in contents[subareas_index+1:]:
        linelist = list(line)
        if linelist[0] == " " or linelist[0] == ";" or len(linelist) < 10:
            continue
        elif line.find('[') != -1:
            break
        else:
            for sub in DelineateNetwork.list_of_subcatchments:
                templine = contents.index(line)
                splitline = contents[templine].split()
                if splitline[0] == sub:
                    splitline[1] = str(guess[DelineateNetwork.list_of_subcatchments.index(sub)][3])
                    splitline[2] = str(guess[DelineateNetwork.list_of_subcatchments.index(sub)][4])
                    splitline[3] = str(guess[DelineateNetwork.list_of_subcatchments.index(sub)][5])
                    splitline[4] = str(guess[DelineateNetwork.list_of_subcatchments.index(sub)][6])
                    splitline[5] = str(guess[DelineateNetwork.list_of_subcatchments.index(sub)][7])
                    contents[templine] = "      ".join(splitline) + '\n'
                    break
    with open(trialfile, 'w') as newfile:
        for i in range(count):
            newfile.write(contents[i])
    newfile.close()
    return


def np_generations(Unionsetlist, observationdatafile, distancefilename, root):
    """Governs the generations process for SWMMCALPY.  For X number of generations, each input file is simulated using
    PySWMM, and then its nearness to the observational data time series is evaluated.  The input files are then ranked
    and selected by a tournament selection for persistence into the next generation.

    :param Unionsetlist:
    :param observationdatafile:
    :param distancefilename:
    :param root:
    :return:
    """
    global solution, iteration

    for iteration in range(FileSettings.geneticdict['generations']):
        print(iteration)
        global P_prime
        P_prime = Main.pool.map(ObjectiveFunctions.Par_objectivefunctions, FileSettings.settingsdict['Unionsetlist'])
        for guess in ObjectiveFunctions.par_rankP_prime():
            if guess == 0:
                print(ObjectiveFunctions.par_aggFunc[ObjectiveFunctions.par_rankP_prime().index(guess)])
                print(Unionsetlist[ObjectiveFunctions.par_rankP_prime().index(guess)])
                solution = Unionsetlist[ObjectiveFunctions.par_rankP_prime().index(guess)]
        next_fillmatingpool()
        crossover_list = []
        for guess in range(len(not_selected_list)):
            crossover_list.append(next_crossover())
        arg_tup = zip(crossover_list, not_selected_list)
        pool = Main.pool_initializer()
        pool.starmap(next_insertguessestoinputfile, arg_tup)
    return
