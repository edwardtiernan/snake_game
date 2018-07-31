import Objective_functions
import Main
import CreateGuesses
import NextGuesses
import FileSettings
import multiprocessing


# Try creating a new function to define nextmatingpool and the mapped next_insertguessestoinputfile()

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
        P_prime = Main.pool.map(Objective_functions.Par_objectivefunctions, FileSettings.settingsdict['Unionsetlist'])
        for guess in Objective_functions.par_rankP_prime():
            if guess == 0:
                print(Objective_functions.par_aggFunc[Objective_functions.par_rankP_prime().index(guess)])
                print(Unionsetlist[Objective_functions.par_rankP_prime().index(guess)])
                solution = Unionsetlist[Objective_functions.par_rankP_prime().index(guess)]
        global nextmatingpool
        nextmatingpool = CreateGuesses.next_fillmatingpool()
        try:
            Main.pool.map(CreateGuesses.next_insertguessestoinputfile, nextmatingpool)
        except IndexError:
            print("IndexError")
    return


def obj_func_writer():
    return
