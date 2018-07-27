import Objective_functions
import CreateGuesses
import NextGuesses
import FileSettings
import multiprocessing

def generations_generator(filelist, Qfilelist, Unionsetlist, observationdatafile, distancefilename, root):
    global solution
    with open('Ob_Func.txt', 'w') as file:
        file.write("NPE        NVE        NSE        NED        Agg\n")
        Objective_functions.objectivefunctions([FileSettings.settingsdict['inputfilename']], observationdatafile, distancefilename, root)
        print(Objective_functions.P_prime)
        file.write("{:.04f}     {:.04f}     {:.04f}     {:.04f}\n".format(Objective_functions.P_prime[0][0]
                                                                                , Objective_functions.P_prime[0][1]
                                                                                , Objective_functions.P_prime[0][2]
                                                                                , Objective_functions.P_prime[0][3]))
        for iteration in range(FileSettings.geneticdict['generations']):
            print(iteration)
            global P_prime
            pool = multiprocessing.Pool(8)
            P_prime = pool.map(Objective_functions.Par_objectivefunctions, FileSettings.settingsdict['Unionsetlist'])
            for guess in Objective_functions.par_rankP_prime():
                if guess == 0:
                    print(Objective_functions.par_aggFunc[Objective_functions.par_rankP_prime().index(guess)])
                    print(Unionsetlist[Objective_functions.par_rankP_prime().index(guess)])
                    solution = Unionsetlist[Objective_functions.par_rankP_prime().index(guess)]
                    file.write("{:.04f}     {:.04f}     {:.04f}     {:.04f}     {:.04f}\n".format(P_prime[
                                                                                      Objective_functions.par_rankP_prime().
                                                                                      index(guess)][0], P_prime[Objective_functions.
                                                                                      par_rankP_prime().index(guess)][1],
                                                                                      P_prime[Objective_functions.par_rankP_prime().
                                                                                      index(guess)][2], P_prime[Objective_functions.
                                                                                      par_rankP_prime().index(guess)][3],
                                                                                      Objective_functions.par_aggregateFunction()
                                                                                      [Objective_functions.par_rankP_prime().index(guess)]))
                    #print(Objective_functions.P_prime[Objective_functions.rankP_prime().index(guess)])
            nextmatingpool = NextGuesses.fillmatingpool(Unionsetlist)
            for infile in nextmatingpool:
                try:
                    Qfile = [NextGuesses.not_selected_list[nextmatingpool.index(infile)]]
                    NextGuesses.read_initial_parameters(infile)
                    NextGuesses.create_next_generation(infile, Qfile, nextmatingpool)
                except IndexError:
                    break
    return

