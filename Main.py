import FileSettings
import DelineateNetwork
import CreateGuesses
import ObjectiveFunctions
import Generations
import os
import multiprocessing
import time


start_time = time.time()


def pool_initializer():
    """ Initializes the multiprocessing variable "pool" that can then be used to .map() the parallelizable functions
    in Generations.py and CreateGuesses.py

    :return pool: a multiprocessing variable that utilizes the number of processors passed by the "multiprocessors"
    keyword in the "settingsdict" dictionary variable.
    """
    global pool
    pool = multiprocessing.Pool(FileSettings.settingsdict['multiprocessors'])
    return pool


def first_generation():
    """Collection of functions that produce the first 200 input files.  They are all generated as straight mutations
    from the same starting point input file.
    :return: 200 input files, "trialfileXXX.inp"
    """

    CreateGuesses.par_creategenerations()
    return


def subsequent_generations():
    """Collection of functions that produce all input files after the first 200.  The observation data file is read to
    be compared to by all other SWMM outputs by input files impregnated with parameter guesses.

    :return: many generations of 200 input files, theoretically converging to minimum objective function guess
    """
    # Objective_functions.readobservationfile()

    CreateGuesses.np_generations(FileSettings.settingsdict['Unionsetlist'],
                                 FileSettings.settingsdict['observationdatafile'],
                                 FileSettings.settingsdict['distancefilename'], FileSettings.settingsdict['root'])
    return


def cleanup():
    """ SWMMCALPY produces 200 .inp files, as well as the accompanying .out and .rpt files.  These are necessary
    while the program is running, but at the end they can be deleted.  The best solution is also renamed.

    :return: fewer superfluous files after SWMMCALPY completes its generations
    """
    filelist = []
    dir_path = os.path.dirname(os.path.realpath("Main.py"))
    for f in os.listdir(dir_path):
        if f.startswith("Calibrated"):
            os.remove(os.path.join(dir_path, f))
        if f.startswith("trialfile") and f != CreateGuesses.solution:
            filelist.append(f)
        if f.endswith("Example1.out"):
            filelist.append(f)
        if f == CreateGuesses.solution:
            os.rename(f, "CalibratedSolution.inp")
    for f in filelist:
        os.remove(os.path.join(dir_path, f))
    return


if __name__ == "__main__":
    pool_initializer()
    first_generation()
    subsequent_generations()
    cleanup()
    print("Time elapsed:", time.time() - start_time)
