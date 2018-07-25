import FileSettings
import DelineateNetwork
import numpy as np

def countsubcatchments(inputfilename=FileSettings.settingsdict['inputfilename']):
    """Establishes a upper limit for the for-loop that parses the SWMM input file"""
    global count
    with open(inputfilename, 'r') as swmmput:
        contents = swmmput.readlines()
        count = len(contents)
    return(count)
countsubcatchments()

def read_initial_parameters(inputfilename):
    """Opens and reads the parameters in the [SUBCATCHMENT] and [SUBAREA] headers within the SWMM input file.
    Adds these parameters (as strings) to a numpy array"""
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

    #Part of the function that experiments with np array.  Potentially removes the need for the list transformation
    #   functions that chew up a lot of time.  Each subcatchment has a row, each parameter type has a column.
    global subcatchment_parameters_np
    subcatchment_parameters_np = np.empty((len(subc_params[0]) + len(subarea_params[0]), len(subc_params)), dtype=float)
    for row in range(len(subc_params)):
        for col in range(len(subc_params[0])):
            subcatchment_parameters_np[row, col] = float(subc_params[row][col])
    for row in range(len(subarea_params)):
        for col in range(len(subarea_params[0])):
            subcatchment_parameters_np[row, col + len(subc_params[0])] = float(subarea_params[row][col])

    #Old string code
    # for i in range(len(subc_params)):
    #     for j in range(len(subarea_params[i])):
    #         subc_params[i].append(subarea_params[i][j])
    #     subcatchment_parameters.append(subc_params[i])
    return(np_subcatchment_parameters)
print(read_initial_parameters(FileSettings.settingsdict['inputfilename']))

def transformation_flatten(twoDlistinput):
    """Old string code that takes any 2D list and maps it to a 1D list by adding each subsequent row to the end
    of the first row"""
    oneDlistoutput = []
    for i in range(len(twoDlistinput)):
        for j in range(len(twoDlistinput[i])):
            oneDlistoutput.append(twoDlistinput[i][j])
    return(oneDlistoutput)

def compile_initial_guess(inputfilename):
    global relevant_subcatchment_indices, relevant_subcatchment_parameters, original_guess_flat
    relevant_subcatchment_indices = []
    for allsub in subc_names:
        for upstreamsub in DelineateNetwork.list_of_subcatchments:
            if allsub == upstreamsub:
                relevant_subcatchment_indices.append(subc_names.index(allsub))
    relevant_subcatchment_parameters = []
    for i in relevant_subcatchment_indices:
        relevant_subcatchment_parameters.append(read_initial_parameters(inputfilename)[i])
    initial_guess_flat = transformation_flatten(relevant_subcatchment_parameters)
    if inputfilename == FileSettings.settingsdict['distancefilename']:
        original_guess_flat = initial_guess_flat

    print(initial_guess_flat)
    return(initial_guess_flat)
compile_initial_guess(FileSettings.settingsdict['inputfilename'])

#This line does what compile_initial_guess does, but with numpy arrays.  It creates an array where each relevant
#   subcatchment is a row and each parameter type is a column.
np_initial_guess_flat = subcatchment_parameters_np[relevant_subcatchment_indices]
print(np_initial_guess_flat)
