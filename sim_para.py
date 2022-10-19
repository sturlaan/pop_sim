import multiprocessing as mp
import os 

number_loop=1000
number_year=29


path=os.path.expanduser('~/Population/g2022')

# the projection uses the end year population information at the "base_year";
# note that in the population.csv this year is corresponds to "year==base_year+1"
# as the file referring to the start of year population.
base_year=2021
start_year=base_year+1

## move_max
## the moving matrix is the same after the year move_max;
move_max=2027


max_year=31
move_age=69
number_region=356
maxage=120
range_fertility=49-15+1


## estimation related 
total_core=mp.cpu_count()
number_core=40
sim_mark="new"

print('total number of available CPUs is', total_core)
