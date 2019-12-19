import os
import filecmp
import numpy as np

iteration_cnt = 20
N = 360

input_path_random = 'rand/rand.txt'
output_path_random = f'rand/periodic/textoutputs/rand_0{iteration_cnt}.txt'

program_output = f'outputs/out_0{iteration_cnt}.txt'

C = 6
num_process = C**2 + 1

print(f'time mpirun -np {num_process} python game.py {input_path_random} {program_output} {iteration_cnt}')
os.system(f'time mpirun -np {num_process} python game.py {input_path_random} {program_output} {iteration_cnt}')

if filecmp.cmp(program_output, output_path_random):
    print('Success')
else:
    print('fail')

    true_out = np.loadtxt(output_path_random, dtype=np.int8)
    prog_out = np.loadtxt(program_output, dtype=np.int8)

    cnt = 0

    for i in range(N):
        for j in range(N):
            if true_out[i][j] != prog_out[i][j]:
                print(i,j, true_out[i][j], prog_out[i][j])
                cnt += 1
    
    print('cnt: ', cnt)
    



