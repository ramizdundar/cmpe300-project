from mpi4py import MPI
import numpy as np
import sys
# mpirun -np 17 python game.py input.txt output.txt 5


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
num_processes = comm.Get_size()
C = np.sqrt(num_processes - 1)
N = 360
size = int(N / C)


def passing_1():
    pass


def passing_2():
    pass


def passing_3():
    pass


def passing_4():
    pass


def recv_from_parent():
    message = np.empty((size, size), dtype=int)
    comm.Recv(message, source=0)
    return message


def send_to_child(child_rank, grid):
    row = int((child_rank-1) // C) * size
    col = int((child_rank-1) % C) * size
    message = np.array(grid[row:row+size, col:col+size], dtype=int)
    comm.Send(message, dest=child_rank)



if rank == 0:

    if len(sys.argv) != 4:
        print('argument count error')

    grid = np.zeros((N, N), dtype=int)

    try:
        inp = open(sys.argv[1])
        for i, line in enumerate(inp):
            row = [int(x) for x in line.split()]
            grid[i] = np.array(row)
    except FileNotFoundError:
        print('File not accessible')

    # check c is integer and even
    if not C.is_integer():
        print('C is not an integer')
        print(f'number of processes is: {num_processes}')
        raise ValueError
    elif C % 2 == 1:
        print('C is not even')
        print(f'number of processes is: {num_processes}')
        raise ValueError
    else:
        C = int(C)
    
    for child_rank in range(1, num_processes):
        send_to_child(child_rank, grid)

    
elif rank % 4 == 1:
    message = recv_from_parent()
    grid = np.zeros((size+2, size+2), dtype=int)
    grid[1:1+size, 1:1+size] = message

elif rank % 4 == 2:
    message = recv_from_parent()
    grid = np.zeros((size+2, size+2), dtype=int)
    grid[1:1+size, 1:1+size] = message

elif rank % 4 == 3:
    message = recv_from_parent()
    grid = np.zeros((size+2, size+2), dtype=int)
    grid[1:1+size, 1:1+size] = message

elif rank % 4 == 0:
    message = recv_from_parent()
    grid = np.zeros((size+2, size+2), dtype=int)
    grid[1:1+size, 1:1+size] = message

else:
    raise RuntimeError

