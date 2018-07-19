import FileSettings
import DelineateNetwork
import CreateGuesses
import Objective_functions
import NextGuesses
import Generations
import os
import multiprocessing
from pympler.tracker import SummaryTracker

tracker = SummaryTracker()

import time
start_time = time.time()


def main():

    DelineateNetwork.subnetwork_subcatchments()

    CreateGuesses.readparametersfromfile()
    CreateGuesses.countsubcatchments()
    CreateGuesses.read_initial_parameters(FileSettings.settingsdict['inputfilename'])
    CreateGuesses.compile_initial_guess(FileSettings.settingsdict['inputfilename'])
    CreateGuesses.compile_initial_guess(FileSettings.settingsdict['distancefilename'])
    CreateGuesses.create_generation(FileSettings.settingsdict['inputfilename'], FileSettings.settingsdict['Unionsetlist'])

    Objective_functions.readobservationfile(FileSettings.settingsdict['observationdatafile'])

    #NextGuesses.read_initial_parameters(FileSettings.settingsdict['inputfilename'])

    Generations.generations_generator(FileSettings.settingsdict['filelist'], FileSettings.settingsdict['Qfilelist'],
                                      FileSettings.settingsdict['Unionsetlist'],
                                      FileSettings.settingsdict['observationdatafile'],
                                      FileSettings.settingsdict['distancefilename'], FileSettings.settingsdict['root'])
    return


def cleanup():
    filelist = []
    dir_path = os.path.dirname(os.path.realpath("Main.py"))
    for f in os.listdir(dir_path):
        if f.startswith("Calibrated"):
            os.remove(os.path.join(dir_path, f))
        if (f.startswith("trialfile") and f != Generations.solution):
            filelist.append(f)
        if (f.endswith("Example1.rpt") or f.endswith("Example1.out")):
            filelist.append(f)
        if f == Generations.solution:
            os.rename(f, "CalibratedSolution.inp")
    for f in filelist:
        os.remove(os.path.join(dir_path, f))
    return


if __name__ == '__main__':
    main()
    cleanup()
    tracker.print_diff()
    print("Time elapsed:", time.time() - start_time)




