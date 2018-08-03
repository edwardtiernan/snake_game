import threading
import multiprocessing


def argument_definer():
    """ Defines two global arguments, one of them is passed as the return.  I THINK that the "global" call should make
    both arguments visible to the Pool function, but that is not what happens."""
    global arg1, arg2
    arg1 = ["string 4", "string 5", "string 6"]
    arg2 = ["string 1", "string 2", "string 3"]
    return


def wants_to_use_arguments(argument):
    """ This is the function that wants to access the arg1 argument"""
    print(argument)
    return


def parallel_function(arg2):
    """ This function gets called by the Pool() multiprocessing function, it calls the function that wants to access
    the globals.  The argument that gets passed by the Pool() function still works fine"""
    print(arg2)
    wants_to_use_arguments(arg1)
    # print(wants_to_use_arguments())
    return


def pool_definer():
    """ First, the function that defines the globals is called.  Then one of those arguments is passed to the pool.map
    function which calls the above arguments.  Ultimately the pool.map seems to destroy the global-ness of arg1 and I
    don't know why."""
    argument_definer()
    # thread1 = threading.Thread(target=parallel_function, args=(arg1, arg2[0]))
    # thread2 = threading.Thread(target=parallel_function, args=(arg1, arg2[1]))
    # thread3 = threading.Thread(target=parallel_function, args=(arg1, arg2[2]))
    #
    # thread1.start()
    # thread2.start()
    # thread3.start()
    pool = multiprocessing.Process(target=parallel_function, args=(args2, ))
    return


if __name__ == '__main__':
    pool_definer()