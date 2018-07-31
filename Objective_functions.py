import FileSettings
import Generations_Numpy
import DelineateNetwork
from pyswmm import Simulation, Nodes
import datetime
import re
import math
import numpy as np
import CreateGuesses


def readobservationfile(observationdatafile=FileSettings.settingsdict['observationdatafile']):
    """ Reads the observationdatafile as a time series and puts it into a list of floats.  This list is later compared
    to the floats parsed from the PySWMM reader of SWMM output.

    :param observationdatafile:
    :return time_difference:
    """
    with open(observationdatafile, 'r') as obs_file:
        global contents
        contents = obs_file.readlines()
        global obs_data, time_difference, obs_time
        obs_data = []
        obs_time = []
        for line in contents:
            linelist = list(line)
            if linelist[0] == ';' or linelist[0] == ' ' or len(list(line)) < 15:
                continue
            else:
                templine = line.split()
                if float(templine[-1]) < 0:
                    obs_data.append(0)
                else:
                    obs_data.append(float(templine[-1]))
                day_templine_preprocessing = line.replace(' ', ';')
                day_templine = re.split('[/|;|:|\t]', day_templine_preprocessing)
                month = int(day_templine[0])
                day = int(day_templine[1])
                year = int(day_templine[2])
                hour = int(day_templine[3])
                minute = int(day_templine[4])
                second = int(day_templine[5])
                if day_templine[6] == 'PM' and hour != 12:
                    hour = hour + 12
                elif day_templine[6] == 'AM' and hour == 12:
                    hour = 0
                obs_time.append(datetime.datetime(year, month, day, hour, minute, second))
        time_difference = obs_time[1] - obs_time[0]
    return time_difference


readobservationfile()


def normalizedpeakerror():
    """ Evaluates the NPE by comparing the maximum of the "obs_data" list of floats to the maximum of the "hydrograph"
    list of floats determined by PySWMMs parser of SWMMs output.
    Requires that readobservationfile() and PySWMM have both been called to initialize "obs_data" and "hydrograph".

    :return peak_error: A float metric of the difference in absolute value between the two compared time series's peaks
    """
    peak_simulation = max(hydrograph)
    peak_observation = max(obs_data)
    peak_error = abs(peak_simulation - peak_observation)/(peak_observation + peak_simulation)
    return peak_error


def normalizedvolumeerror():
    """ Evaluates the NVE by comparing the trapezoidal approximation of the list of floats contained within "obs_data"
    and "hydrograph"
    Requires that readobservationfile() and PySWMM have both been called to initialize "obs_data" and "hydrograph".

    :return volume_error: A float metric of the difference in absolute value between the two compared time series's
    volume approximations
    """
    volume_simulation = 0
    volume_observation = 0
    for sim_index in range(1,len(hydrograph)):
        volume_simulation_trapezoid = (hydrograph[sim_index-1]+hydrograph[sim_index])*simulation_timestep/2
        volume_simulation = volume_simulation + volume_simulation_trapezoid
    for data_index in range(1,len(obs_data)):
        volume_observation_trapezoid = (obs_data[data_index-1]+obs_data[data_index])*time_difference.total_seconds()/2
        volume_observation = volume_observation + volume_observation_trapezoid
    volume_error = abs(volume_simulation-volume_observation)/(volume_simulation + volume_observation)
    return volume_error


def nashsutcliffe():
    """Evaluates the NSE_m by computing the ratio of the difference of "obs_data" and "hydrograph" at each index to the
    difference between "obs_data" and its own average.
    Requires that readobservationfile() and PySWMM have both been called to initialize "obs_data" and "hydrograph".

    :return NSE_m: A float metric of the ratio between the predictive power of the model and the predictive power of
    simply the average of the observed data
    """
    average_obs = sum(obs_data)/len(obs_data)
    sum_sim_obs = 0
    sum_obs_obsave = 0
    for i in range(len(min(obs_data, hydrograph))-1):
        diff_sim_obs = (obs_data[i] - hydrograph[i])**2
        sum_sim_obs = sum_sim_obs + diff_sim_obs
        diff_obs_obsave = (obs_data[i] - average_obs)**2
        sum_obs_obsave = sum_obs_obsave + diff_obs_obsave
    mNSE = sum_sim_obs/sum_obs_obsave
    return mNSE


def NED(trialfilename):
    """ Evaluates the NED by computing the euclidean distance from the origin of the vector composed of the
    maximum-normalized difference between each element of the guess input file and the "distancefilename"

    :param trialfilename: the guess input file whose spatial relationship to the "distancefilename" is being assessed
    :return NED: A float metric of the distance between the two guesses in the feasible parameter space
    """
    random_guess = CreateGuesses.compile_initial_guess(trialfilename)
    initial_guess = CreateGuesses.compile_initial_guess(FileSettings.settingsdict['distancefilename'])
    sum = 0
    count_m = random_guess.size
    for i in range(len(initial_guess)):
        for j in range(len(initial_guess[0])):
            num = abs(initial_guess[i][j] - random_guess[i][j])
            denom = initial_guess[i][j] + random_guess[i][j]
            ratio = (num/denom)**2
            sum = sum + ratio
    NED = math.sqrt(sum)/count_m
    return NED


def objectivefunctions(filelist, observationdatafile, distancefilename, root):
    """ This function does the same thing as Par_objectivefunctions() with the exception being that it accepts a list
    of strings as an argument and not a string.  This means it is not parallelizable, but still used in the cross-over
    operation to determine which of the guesses is better.

    :param filelist:
    :param observationdatafile:
    :param distancefilename:
    :param root:
    :return:
    """
    global hydrograph, simulation_timestep, sim_time, P_prime
    P_prime = []
    for trialfile in filelist:
        hydrograph = []
        sim_time = []
        with Simulation(trialfile) as sim:
            node_object = Nodes(sim)
            root_location = node_object[root]
            simulation_timestep = time_difference.total_seconds()
            sim.step_advance(simulation_timestep)
            for step in sim:
                sim_time.append(sim.current_time)
                hydrograph.append(root_location.total_inflow)
        objFunc = [normalizedpeakerror(), normalizedvolumeerror(), nashsutcliffe(), NED(trialfile)]
        P_prime.append(objFunc)
    return objFunc


def Par_objectivefunctions(trialfile, root=FileSettings.settingsdict['root']):
    """ This function defines the PySWMM operations that occur for each "trialfile". "Hydrograph" list of floats is
    defined by calling the SWMM module and assigning the output at each time step to the list. Then each objective
    function is called and the values are put into a list "objFunc"

    This function is called in parallel by SWMMCALPY, each "trialfile" can be evaluated independently.

    :param trialfile:
    :param root: necessary to tell PySWMM where to read the total inflow output from
    :return objFunc: list of floats that gets mapped by the multiprocessing.Pool()
    """
    global hydrograph, simulation_timestep, sim_time
    hydrograph = []
    sim_time = []
    with Simulation(trialfile) as sim:
        node_object = Nodes(sim)
        root_location = node_object[root]
        simulation_timestep = time_difference.total_seconds()
        sim.step_advance(simulation_timestep)
        for step in sim:
            sim_time.append(sim.current_time)
            hydrograph.append(root_location.total_inflow)
    objFunc = [normalizedpeakerror(), normalizedvolumeerror(), nashsutcliffe(), NED(trialfile)]
    #P_prime.append(objFunc)
    return(objFunc)


def aggregateFunction():
    """ This function takes the 2D list "P_prime", which contains the 4 objective function values for each guess, and
    transforms it into a 1D list that contains the aggregate of those objective function values with the weights.  Only
    used in conjunction with objectivefunctions() because they are not parallelizable.

    :return:
    """
    global aggFunc
    aggFunc = []
    for objFunc in P_prime:
        aggFunc.append(objFunc[0]*FileSettings.settingsdict['weights'][0] + objFunc[1]*FileSettings.settingsdict['weights'][1] +
                       objFunc[2]*FileSettings.settingsdict['weights'][2] + objFunc[3]*FileSettings.settingsdict['weights'][3])
    return aggFunc


def par_aggregateFunction():
    global par_aggFunc
    par_aggFunc = []
    for objFunc in Generations_Numpy.P_prime:
        par_aggFunc.append(objFunc[0] * FileSettings.settingsdict['weights'][0] +
                           objFunc[1] * FileSettings.settingsdict['weights'][1] +
                           objFunc[2] * FileSettings.settingsdict['weights'][2] +
                           objFunc[3] * FileSettings.settingsdict['weights'][3])
    return par_aggFunc


def rankP_prime():
    x = aggregateFunction()
    seq = sorted(x)
    index = [seq.index(v) for v in x]
    return index


def par_rankP_prime():
    x = par_aggregateFunction()
    seq = sorted(x)
    index = [seq.index(v) for v in x]
    return index




