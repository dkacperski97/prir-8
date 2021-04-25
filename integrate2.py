from mpi4py import MPI
import sys

def checkInput(id):
    numArguments = len(sys.argv)
    if numArguments != 4:
        if id == 0:
            print("Nie podano wymaganych argumentów. Przykład: python integrate2.py begin end num_points")
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
        it = iter(parts)
        my_part = next(it)
        for index, part in enumerate(it):
            # print("send", index+1)
            comm.isend([begin, od, part], dest=index+1)
        my_result = rectangular_integration(begin, od, my_part)
        reqs = []
        # print(begin, od, my_part)
        for i in range(numProcesses-1):
            # print("recv", i+1)
            reqs.append(comm.irecv(source=i+1))
        results = MPI.Request.waitall(reqs)
        results.append(my_result)
        results_sum = sum(results)
        # print(results)
        print("Wynik: {}".format(results_sum))
    else :
        receivedValue = comm.irecv(source=0).wait()
        begin = receivedValue[0]
        od = receivedValue[1]
        part = receivedValue[2]
        result = rectangular_integration(begin, od, part)
        comm.isend(result, dest=0)

########## Run the main function
main()