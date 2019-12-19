# Ramiz Dündar 2016400012
# Compiling
# Working
# Note that method names and variable names are self explanatory
# If you need further understanding please take a look the project
# report where every variable and function is explained in detail
from mpi4py import MPI
import numpy as np
import sys
import pdb
np.set_printoptions(edgeitems=10)
# mpirun -np 17 python game.py input.txt output.txt 5

# necessary variables for all processes
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
num_processes = comm.Get_size()
C = np.sqrt(num_processes - 1)
N = 360
T = int(sys.argv[3])
# size of small grid inside one process (without adding messages)
size = int(N / C)
grid = np.zeros((size+2, size+2), dtype=np.int8)
recieved_from = {
        'up' : np.empty(size, dtype=np.int8),
        'down' : np.empty(size, dtype=np.int8),
        'left' : np.empty(size, dtype=np.int8),
        'right' : np.empty(size, dtype=np.int8),
        'leftup' : np.empty((), dtype=np.int8),
        'rightup' : np.empty((), dtype=np.int8),
        'leftdown' : np.empty((), dtype=np.int8),
        'rightdown' : np.empty((), dtype=np.int8)
}


# variables for targets and tags
rank -= 1

up_target = (rank - C) % C**2 + 1
up_tag = 1
down_target = (rank + C) % C**2 + 1
down_tag = 2
left_target = (rank//C)*C + (rank-1)%C + 1
left_tag = 3
right_target = (rank//C)*C + (rank+1)%C + 1
right_tag = 4

leftup_target = ((rank//C-1)%C)*C + (rank-1)%C + 1
leftup_tag = 5
rightup_target = ((rank//C-1)%C)*C + (rank+1)%C + 1
rightup_tag = 6
leftdown_target = ((rank//C+1)%C)*C + (rank-1)%C + 1
leftdown_tag = 7
rightdown_target = ((rank//C+1)%C)*C + (rank+1)%C + 1
rightdown_tag = 8

rank += 1


def update_messages(rank,grid):

    up_message = np.array(grid[1, 1:1+size], dtype=np.int8)
    down_message = np.array(grid[size, 1:1+size], dtype=np.int8)
    left_message = np.array(grid[1:1+size, 1], dtype=np.int8)
    right_message = np.array(grid[1:1+size, size], dtype=np.int8)

    leftup_message = np.array(grid[1, 1], dtype=np.int8)
    rightup_message = np.array(grid[1, size], dtype=np.int8)
    leftdown_message = np.array(grid[size, 1], dtype=np.int8)
    rightdown_message = np.array(grid[size, size], dtype=np.int8)

    messages = {
        'up' : up_message,
        'down' : down_message,
        'left' : left_message,
        'right' : right_message,
        'leftup' : leftup_message,
        'rightup' : rightup_message,
        'leftdown' : leftdown_message,
        'rightdown' : rightdown_message
    }

    return messages


def grid_update(recieved_from, grid):

    grid[0, 1:1+size] = recieved_from['up']
    grid[-1, 1:1+size] = recieved_from['down']
    grid[1:1+size, 0] = recieved_from['left']
    grid[1:1+size, -1] = recieved_from['right']

    grid[0, 0] = recieved_from['leftup']
    grid[0, -1] = recieved_from['rightup']
    grid[-1, 0] = recieved_from['leftdown']
    grid[-1, -1] = recieved_from['rightdown']

def total_neigbour(i, j, grid):

    tot = (
        grid[i-1][j-1]
        + grid[i-1][j]
        + grid[i-1][j+1]
        + grid[i][j-1]
        + grid[i][j+1]
        + grid[i+1][j-1]
        + grid[i+1][j]
        + grid[i+1][j+1]
    )

    return tot


def game_loop(grid):

    temp_grid = np.array(grid[1:1+size, 1:1+size])

    for i in range(size):
        for j in range(size):

            total = total_neigbour(i+1, j+1, grid)

            if total < 2:
                temp_grid[i][j] = 0
            if total > 3:
                temp_grid[i][j] = 0
            if total == 3:
                temp_grid[i][j] = 1


    grid[1:1+size, 1:1+size] = temp_grid


def passing_1(rank, grid):

    messages = update_messages(rank, grid)

    comm.Send(messages['up'], dest=up_target, tag=up_tag)
    comm.Send(messages['down'], dest=down_target, tag=down_tag)
    comm.Send(messages['left'], dest=left_target, tag=left_tag)
    comm.Send(messages['right'], dest=right_target, tag=right_tag)
    comm.Send(messages['leftup'], dest=leftup_target, tag=leftup_tag)
    comm.Send(messages['rightup'], dest=rightup_target, tag=rightup_tag)
    comm.Send(messages['leftdown'], dest=leftdown_target, tag=leftdown_tag)
    comm.Send(messages['rightdown'], dest=rightdown_target, tag=rightdown_tag)

    comm.Recv(recieved_from['up'], source=up_target, tag=down_tag)
    comm.Recv(recieved_from['down'], source=down_target, tag=up_tag)
    comm.Recv(recieved_from['left'], source=left_target, tag=right_tag)
    comm.Recv(recieved_from['right'], source=right_target, tag=left_tag)
    comm.Recv(recieved_from['leftup'], source=leftup_target, tag=rightdown_tag)
    comm.Recv(recieved_from['rightup'], source=rightup_target, tag=leftdown_tag)
    comm.Recv(recieved_from['leftdown'], source=leftdown_target, tag=rightup_tag)
    comm.Recv(recieved_from['rightdown'], source=rightdown_target, tag=leftup_tag)
    
    grid_update(recieved_from, grid)

    game_loop(grid)
    
    
def passing_2(rank, grid):

    messages = update_messages(rank, grid)

    comm.Recv(recieved_from['right'], source=right_target, tag=left_tag)
    comm.Recv(recieved_from['left'], source=left_target, tag=right_tag)

    comm.Send(messages['right'], dest=right_target, tag=right_tag)
    comm.Send(messages['left'], dest=left_target, tag=left_tag)

    comm.Send(messages['up'], dest=up_target, tag=up_tag)
    comm.Send(messages['down'], dest=down_target, tag=down_tag)
    comm.Send(messages['leftup'], dest=leftup_target, tag=leftup_tag)
    comm.Send(messages['rightup'], dest=rightup_target, tag=rightup_tag)
    comm.Send(messages['leftdown'], dest=leftdown_target, tag=leftdown_tag)
    comm.Send(messages['rightdown'], dest=rightdown_target, tag=rightdown_tag)

    comm.Recv(recieved_from['up'], source=up_target, tag=down_tag)
    comm.Recv(recieved_from['down'], source=down_target, tag=up_tag)
    comm.Recv(recieved_from['leftup'], source=leftup_target, tag=rightdown_tag)
    comm.Recv(recieved_from['rightup'], source=rightup_target, tag=leftdown_tag)
    comm.Recv(recieved_from['leftdown'], source=leftdown_target, tag=rightup_tag)
    comm.Recv(recieved_from['rightdown'], source=rightdown_target, tag=leftup_tag)

    grid_update(recieved_from, grid)

    game_loop(grid)
    

def passing_3(rank, grid):

    messages = update_messages(rank, grid)

    comm.Recv(recieved_from['down'], source=down_target, tag=up_tag)
    comm.Recv(recieved_from['up'], source=up_target, tag=down_tag)

    comm.Recv(recieved_from['rightdown'], source=rightdown_target, tag=leftup_tag)
    comm.Recv(recieved_from['leftdown'], source=leftdown_target, tag=rightup_tag)
    comm.Recv(recieved_from['rightup'], source=rightup_target, tag=leftdown_tag)
    comm.Recv(recieved_from['leftup'], source=leftup_target, tag=rightdown_tag)

    comm.Send(messages['down'], dest=down_target, tag=down_tag)
    comm.Send(messages['up'], dest=up_target, tag=up_tag)

    comm.Send(messages['rightdown'], dest=rightdown_target, tag=rightdown_tag)
    comm.Send(messages['leftdown'], dest=leftdown_target, tag=leftdown_tag)
    comm.Send(messages['rightup'], dest=rightup_target, tag=rightup_tag)
    comm.Send(messages['leftup'], dest=leftup_target, tag=leftup_tag)
    
    comm.Send(messages['left'], dest=left_target, tag=left_tag)
    comm.Send(messages['right'], dest=right_target, tag=right_tag)

    comm.Recv(recieved_from['left'], source=left_target, tag=right_tag)
    comm.Recv(recieved_from['right'], source=right_target, tag=left_tag)
    
    grid_update(recieved_from, grid)

    game_loop(grid)


def passing_4(rank, grid):

    messages = update_messages(rank, grid)

    comm.Recv(recieved_from['rightdown'], source=rightdown_target, tag=leftup_tag)
    comm.Recv(recieved_from['leftdown'], source=leftdown_target, tag=rightup_tag)
    comm.Recv(recieved_from['rightup'], source=rightup_target, tag=leftdown_tag)
    comm.Recv(recieved_from['leftup'], source=leftup_target, tag=rightdown_tag)

    comm.Recv(recieved_from['down'], source=down_target, tag=up_tag)
    comm.Recv(recieved_from['up'], source=up_target, tag=down_tag)

    comm.Recv(recieved_from['right'], source=right_target, tag=left_tag)
    comm.Recv(recieved_from['left'], source=left_target, tag=right_tag)

    comm.Send(messages['rightdown'], dest=rightdown_target, tag=rightdown_tag)
    comm.Send(messages['leftdown'], dest=leftdown_target, tag=leftdown_tag)
    comm.Send(messages['rightup'], dest=rightup_target, tag=rightup_tag)
    comm.Send(messages['leftup'], dest=leftup_target, tag=leftup_tag)

    comm.Send(messages['down'], dest=down_target, tag=down_tag)
    comm.Send(messages['up'], dest=up_target, tag=up_tag)

    comm.Send(messages['right'], dest=right_target, tag=right_tag)
    comm.Send(messages['left'], dest=left_target, tag=left_tag)

    grid_update(recieved_from, grid)

    game_loop(grid)


def recv_from_parent(grid):
    message = np.empty((size, size), dtype=np.int8)
    comm.Recv(message, source=0)
    grid[1:1+size, 1:1+size] = message


def send_to_child(child_rank, grid):
    row = int((child_rank-1) // C) * size
    col = int((child_rank-1) % C) * size
    message = np.array(grid[row:row+size, col:col+size], dtype=np.int8)
    comm.Send(message, dest=child_rank)

def send_to_main(grid):
    message = np.array(grid[1:1+size, 1:1+size])
    comm.Send(message, dest=0)

def recv_from_child(child_rank, grid):
    message = np.empty((size, size), dtype=np.int8)
    comm.Recv(message, source=child_rank)
    row = int((child_rank-1) // C) * size
    col = int((child_rank-1) % C) * size
    grid[row:row+size, col:col+size] = message

if rank != 0:
    recv_from_parent(grid)
    row = int((rank-1) // C)
    col = int((rank-1) % C) 

if rank == 0:

    if len(sys.argv) != 4:
        print('argument count error')

    grid = np.zeros((N, N), dtype=np.int8)

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

    for child_rank in range(1, num_processes):
        recv_from_child(child_rank, grid)

    np.savetxt(sys.argv[2], grid, fmt='%d', encoding='utf-8', newline=' \n')
    
elif row % 2 == 0 or col % 2 == 0:
    for _ in range(T):
        passing_1(rank, grid)

elif row % 2 == 0 or col % 2 == 1:
    for _ in range(T):
        passing_2(rank, grid)

elif row % 2 == 1 or col % 2 == 0:
    for _ in range(T):
        passing_3(rank, grid)

elif row % 2 == 1 or col % 2 == 1:
    for _ in range(T):
        passing_4(rank, grid)

else:
    print('code should not reach here')
    raise RuntimeError

if rank != 0:
    send_to_main(grid)
