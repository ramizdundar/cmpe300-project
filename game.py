from mpi4py import MPI
import numpy as np
import sys

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
C = comm.Get_size()
N = 360

def passing_1():
    pass

def passing_2():
    pass

def passing_3():
    pass

def passing_4():
    pass

def recv_from_parent():
    pass

def send_to_child(child_rank):
    pass


if rank == 0:

    if len(sys.argv) != 4:
        print('argument count error')

    grid = np.zeros((N, N))

    try:
        inp = open(sys.argv[1])
        for i, line in enumerate(inp):
            row = [int(x) for x in line.split()]
            grid[i] = np.array(row)
    except FileNotFoundError:
        print('File not accessible')
    
    for child_rank in range(1, C):
        send_to_child(child_rank)
    
    
elif rank % 4 == 0:
    recv_from_parent()
elif rank % 4 == 1:
    recv_from_parent()
elif rank % 4 == 2:
    recv_from_parent()
elif rank % 4 == 3:
    recv_from_parent()

