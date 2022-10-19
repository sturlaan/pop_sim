# I want a file with a few different policy relavant population aggregates:
#  Total population 
#  Population in childcare age (1-5 at end of year)  
#  Population in primary school age (age 6-12 at the end of year)  
#  Population in lower secondary school age (age 13-15 at the end of year)  
#  Elderly population (80+ at end of year)
#  Very old population (90+ at end of year)

# We should have one observation of the number of people in these groups across all municipalities, 
# years and simulations. Returning a file with variables: knr, year, sim_id, pop_all, pop0105, pop0612, 
# pop1315, pop8000 pop9000 and 10m obs (356*29*1000). 


### libary importation and some global parameters:

import numpy as np
import pandas as pd
import os 
import copy
import pickle


pd.set_option('float_format', '{:f}'.format)

import sim_para



# maxage=120
# range_fertility=49-15+1
# max_year=31
# number_region=356
# move_age=69


sim_mark=sim_para.sim_mark

path = sim_para.path
max_year=sim_para.max_year
base_year=sim_para.base_year
move_age=sim_para.move_age
number_region=sim_para.number_region
maxage=sim_para.maxage
range_fertility=sim_para.range_fertility
start_year=sim_para.start_year
png_dir=path+'/gif_dir/'

## simulation results are saved with suffixes 'xxx' so that different 
## simulation runs can be used

# run_index_list=['2', '3', '4']
run_index_list=[str(i) for i in range(sim_para.number_loop)]
#for i in range(4):
#    run_index_list.pop(0)

## select the three regions

region_selection=[0, 22, 122, 227]
region_name=['Oslo','Utsira', 'Eidsvoll', 'Bygland']

Region_label=["county "+str(i)+" " for i in range(1, number_region+1)]
Region_label[122]='Eidsvoll'  
Region_label[0]='Oslo'  
Region_label[22]='Utsira'
Region_label[227]='Bygland'  
Region_label.append("nationwide ")


res=[]
## read in the simulatin rsults
for index in run_index_list:
    file = open(path+'/sim_out'+sim_mark+index+'.pkl', 'rb')
    res.append(pickle.load(file))
    file.close()


## find out the number of simulations and number of prediction years
number_loop=len(res)
print('simulation number ',number_loop)
number_year=len(res[0][0])-1
print("simulate %s years" % number_year)

## separate the informations

'''
# the structure of the output
# list 
## first level: index simulation runs, list [number_loop]
## second level: [0] summary of population, list [number_year]
                         3 dimensional array [age, sex, region]
                 [1] summary of immigrants, list [number_year]
                         3 dimensional array [age, sex, region]
                 [2] summary of newborns, 
                         2 dimensional array [sex, region]
                 [3] summary of deaths,     
                         3 dimensional array [age, sex, region]
                 [4] summary of outmigrants,
                         3 dimensional array [age, sex, region]                
                 [5] summary of in-country mover,
                         4 dimensional array [age, sex, region, 2]
We reorganize this to 5 listst ,which correspond to the above 5 different information and have the same structure
'''


list_out=[]
for i in range(number_loop):
    print("loop nr. ", i)
    for j in range(number_year):
        temp=res[i][0][j+1]
        for r in range(number_region):
        # loop, projection year, region, total population, childcare,primary, lower, elderly,over90
            list_temp=[i+1, start_year+j, r, np.sum(temp[:,:,r]), np.sum(temp[1:6,:,r]), np.sum(temp[6:13,:,r]),  np.sum(temp[13:16,:,r]), np.sum(temp[80:,:,r]), np.sum(temp[90:,:,r])]
            list_out.append(list_temp)

test_out=pd.DataFrame(list_out)

print("df generated")

df_knr=pd.read_csv(path+'/'+'df_knr.csv')

test_out.set_axis(["sim_id", "year", "region", "pop_all", "pop0105", "pop0612", "pop1315", "pop8000", "pop9000"], axis=1, inplace=True)

df_uncertainty=test_out.merge(df_knr, on='region')
df_uncertainty.drop(columns=['region'], inplace=True)

df_uncertainty.to_csv(path+'/'+'uncertainty_sim.csv', index=False)

            

        
        
        



