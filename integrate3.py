from mpi4py import MPI
import sys

def checkInput(id):
    numArguments = len(sys.argv)
    if numArguments != 4:
        if id == 0:
            print("Nie podano wymaganych argumentów. Przykład: python integrate3.py begin end num_points")
        sys.exit()

def integrated_function(x):
    return x*x

def rectangular_integration(begin, od, part):
    return sum(map(lambda x: integrated_function(begin+x*od) * od, part))

def get_parts(A, threads):
    size = int(len(A) / threads)
    rest = len(A) % threads
    result = []
    iterator = iter(A)
    for i in range(threads):
        result.append([])
        for j in range(size):
            result[i].append(next(iterator))
        if rest:
            result[i].append(next(iterator))
            rest -= 1
    return result

def main():
    comm = MPI.COMM_WORLD
    id = comm.Get_rank()            #number of the process running the code
    numProcesses = comm.Get_size()  #total number of processes running
    myHostName = MPI.Get_processor_name()  #machine name running the code

    checkInput(id)
    
    if id == 0:
        begin = float(sys.argv[1])
        end = float(sys.argv[2])
        num_points = int(sys.argv[3])
        parts = get_parts(range(1, num_points + 1), numProcesses)
        od = (end - begin) / num_points
        data = [[begin, od, p] for p in parts]
    else:
        data = None

    data = comm.scatter(data, root=0)
    begin = data[0]
    od = data[1]
    part = data[2]
    result = rectangular_integration(begin, od, part)
    results = comm.gather(result, root=0)

    if id == 0:
        results_sum = sum(results)
        print("Wynik: {}".format(results_sum))

########## Run the main function
main()