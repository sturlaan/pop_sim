import multiprocessing as mp

number_loop=1000
number_year=30


total_core=mp.cpu_count()
number_core=40
sim_mark="new"

print('total number of available CPUs is', total_core)
