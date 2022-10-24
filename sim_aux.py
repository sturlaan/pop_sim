# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 13:01:41 2020

The python script to pimplement micro simulation model for regional
population projection for norwegian population.

@author: jia


*** revised on Tue, 20,10, 2020

Use the same data inputs as the regional projection implemented by Stula and Stefan.

Data input: see email from Sturla, 16,10,2020 "Input for microsimulation"

** revised on Wed, 10,03,2021
Adjust the outmigration rate so that the mean of out-migrants is the same as the 
national projection level. 

see mail exchange with Sturla 10,03,2021

** revised on Wed, 10,09,2021
1. adjust the birth gender ratio (0.5 to 0.51369)
2. make sure that females who give birth also subjected to mortarlity\outmigration\internal-moving risk

see mail exchange with Sturla 10,09,2021

** revised on Wed, 01,10,2021
adjust the timing of events: mortality, internal moving and external outmigration are modelled simultaneously. 

see mail exchange with Sturla 10,09,2021


"""
### libary importation and some global parameters:

import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as spo
import pandas as pd
import subprocess
import os 
from itertools import compress
import copy
import pickle
import math
import multiprocessing as mp
import time
import sim_para
from dapla import FileClient

# number of simulations and total year of projection 
# is defined in sim_para.py

number_loop=sim_para.number_loop
number_year=sim_para.number_year
sim_mark=sim_para.sim_mark
max_year=sim_para.max_year
base_year=sim_para.base_year
start_year=sim_para.start_year
move_age=sim_para.move_age
number_region=sim_para.number_region
maxage=sim_para.maxage
range_fertility=sim_para.range_fertility
move_max=sim_para.move_max
workpath=sim_para.workpath


pd.set_option('float_format', '{:f}'.format)

# path = os.path.expanduser('/ssb/stamme02/regfram/sim/wk48/g2022')
path = sim_para.path
# path="C:\\Users\\jia\\Dropbox\\PopulationProjection\\Population\\"
# path="C:\\Users\\sal\\Dropbox\\Work\\PopulationProjection\\"



# bins=maxage//5
bins=maxage

## number of regions

## in this version, we are on county levels

print("baseyear is set to: ", base_year)
print("localpath is set to: ", path)
print("data will be saved to: ", workpath)

p_region=np.zeros(number_region)
ind_id=0



# The individual class

class individual(object):
    """ An individual which have the following properties:
     Attributes:
        age:
        sex: [0,1]
        Region:  356 different regions (kommune in norway)
        # POB: place of birth [0,1,...,356] 356: foreign born
        # age_im:  age of immigration, native -1
        status_birth: [0,1] 0:normal, 1, giving birth
        status:  [0,1, 2], 0:normal, 1 dead 2, outmigrate, 3 internal movement
        time_index: year of simulation. base_year = -1   
        
    """
    
    def __init__(self, age=0, sex=0, region=0, status_birth=0, status=0, time_index=-1):
        """
        return a individual
        set initial values 
        """
        global ind_id
        self.id=ind_id
        ind_id=ind_id+1
        
        self.age=age
        self.sex=sex
        self.region=region
        self.status=status
        self.status_birth=status_birth
        self.time_index=time_index
        self.age_im=-1
        self.region_old=region
        self.fertile=0

       
    def birth(self, fertility_table):
        """
        15-49 years old.
        """
        region=self.region
        self.fertile=0
        self.status_birth=0
        time_index=self.time_index
        if (self.sex == 1) and (self.age >=15)  and (self.age<=49):
            self.fertile=1
            index=self.age-15
            birth=int(np.random.uniform(0,1000)<=fertility_table[time_index][region, index]*1000)
            #birth=int(np.random.uniform(0,1000)<=50)
            self.status_birth=1*birth
        return self
                 
    # def group_link(self, table_link_a, table_link_r):
        # sex=self.sex
        # age=self.age
        # region=self.region
        # agesex_gr=table_link_a[sex,age]
        # # if region=356 then immigrants, and origin_gr is set to zero
        # origin_gr=table_link_r[region]
        # #if region==number_region:
        # #    print('origin group for immigrant is set to ', origin_gr)
        # return [origin_gr, agesex_gr]
    def group_link(self, table_link_a, table_link_r):
        sex=self.sex
        age=self.age
        region=self.region
        agesex_gr=table_link_a[sex,age]
        return [region, agesex_gr]        
    
     
    def death_move_outmigrate(self, mortality_table, outmigration_table, adjust_factor, move_table):
        """
        Mortality 
        """
        sex=self.sex
        age=self.age
        region=self.region
        time_index=self.time_index
        d_death=0
        d_move=0
        d_out=0
        d_im=0
        
        # default value 
        out_rate=0
        move_rate=0
        
        if (region<number_region):  # native 
            if age>=(maxage-1):  #over maximum age
                d_death=1
            else:
                death_rate=mortality_table[time_index][region,sex,age]*1000
                event_draw=np.random.uniform(0,1000)
                if (age<=move_age):
                    out_rate=outmigration_table[time_index][region,sex,age]*adjust_factor*1000
                    move_rate=move_table[time_index][region,sex,age]*1000
                if event_draw<=death_rate:
                    d_death=1
                else:
                    if event_draw<=death_rate+out_rate:
                        d_out=1
                    else:
                        if event_draw<=death_rate+out_rate+move_rate:
                            d_move=1
        else: # immigrants
            d_im=1
            

        self.status=1*d_death+2*d_out+3*d_move+4*d_im
        return self
             
    
    def move_assign(self, mov_mat,table_link_a,table_link_r):
        ## move or not
        sex=self.sex
        age=self.age
        region=self.region
        time_index=self.time_index
        
        # move to new region if d_move==1 or d_im==1
        move=(self.status>=3)       
        
        if move==1: 
            ## marks the old region before moving
            self.region_old=self.region
            ## destination
            ## [origin_gr, agesex_gr]=self.group_link(table_link_a, table_link_r) 
            [origin_gr, agesex_gr]=self.group_link(table_link_a, table_link_r) 
            ## origin_gr, origin region; agesex_gr, age/sex group
            # origin_gr for region=356 (number_region) is set to zero by default
            time_index_temp=time_index
            if (time_index>move_max-start_year):
                time_index_temp=move_max-start_year 
            move_prob=mov_mat[time_index_temp][int(origin_gr), int(agesex_gr),:]
            region_new=np.random.choice(number_region,p=move_prob)
            self.region=region_new
        return self
        
    
    def step_aging(self): 
        # get the age, time index 
        age=self.age
        time_index=self.time_index
        region=self.region
        
        ## update age, time index and status
        self.age=age+1
        self.region_old=region
        self.time_index=time_index+1
        self.status=0
        
        return self
        
    
    def step_other(self, model, adjust_factor):  

        # assign the status variable for death, outmigrate, and internal moving
        self=self.death_move_outmigrate(model.mortality_table, model.outmigration_table, adjust_factor, model.move_table)

        # assign the new regions.
        self=self.move_assign(model.mov_mat, model.table_link_a, model.table_link_r)

        return self

            
        
# The population class
class population():
    """ a set(list) of individuals at a given time:
 
    Attributes:
    
        member: a list of indiviudals 
        size: number of individuals in this population
        summary: 3 dimensional array (22*2*number_region) which contains the summary information out individuals 
            # axis 0: age groups (in 5 years interval)
            # axis 1: gender
            # axis 2: the region
        im_summary: similar to summary, but keep track of immigrants 
        number_newborn: number of newborns for each region.
        adjust_factor: the adjust factor for the emigration rates (email from Sturla 10.03.2021)
        time_index: 
        
    """
    def __init__(self):
        self.member=[] 
        self.size=0
        self.summary=np.zeros([bins,2,number_region])
        self.number_newborn=np.zeros([2,number_region])
        self.im_summary=np.zeros([move_age+1,2,number_region])
        self.dead_summary=np.zeros([bins,2,number_region])
        self.out_summary=np.zeros([move_age+1,2,number_region])
        self.move_summary=np.zeros([move_age+1,2,number_region,2])
        self.adjust_factor=1
        self.time_index=-1
        self.women_fertile=0
        self.women_fertile_actual=0
    
    def set_timeindex(self):
        time_index=self.member[0].time_index
        self.time_index=time_index
        
    def set_adjust(self,outmigration_table,outmig_size):
        move_pop=np.zeros([move_age+1,2,number_region])
        temp_size=len(self.member)
        for i in range(temp_size):
            index0=self.member[i].age
            if index0<=move_age:
                index1=self.member[i].sex
                index2=self.member[i].region
                move_pop[index0,index1,index2] += 1
        #print(move_pop.shape)
        #print(outmigration_table.shape)
        move_pop2=np.zeros([move_age+1,2,number_region])
        for i in range(move_age+1):
            for j in range(2):
                for k in range(number_region):
                    #print(i, j, k)
                    move_pop2[i,j,k]=move_pop[i,j,k]*outmigration_table[k,j,i]
        simu_size=np.sum(move_pop2)
        self.adjust_factor=outmig_size/simu_size
    
    def remove_exit(self):
        self.member=[ind for ind in self.member if (ind.status==0 or ind.status==3 or ind.status==4)]
        self.size=len(self.member)
        
        
    def setup_newborn(self,ind):
        newborn=individual()
        newborn.age=0
        newborn.sex=int(np.random.uniform()>0.51369)
        newborn.region=ind.region
        newborn.region_old=ind.region
        newborn.time_index=ind.time_index
        return newborn
        
    
    def add_newborn(self):
        # new borns
        list_preg=[ind for ind in self.member if ind.status_birth==1]
        size_a=len(list_preg)
        list_newborn=[self.setup_newborn(ind) for ind in list_preg]
        size_b=len(list_newborn)
        if size_a!=size_b:
            print("error", self.time_index)
        self.member.extend(list_newborn)
        return list_newborn

    def setup_immigrant(self, im_dist_table):
        time_index=self.member[0].time_index
        immigrant=individual() 
        agesex_prob=im_dist_table[time_index][:]
        agesex=np.random.choice((move_age+1)*2,p=agesex_prob)
        immigrant.time_index=time_index
        immigrant.sex=agesex//(move_age+1)
        immigrant.age=(agesex%(move_age+1))
        immigrant.age_im=(agesex%(move_age+1))
        # immigrant's region is initially set to 356
        immigrant.POB=number_region
        immigrant.region=number_region
        immigrant.region_old=number_region
        return immigrant

    def add_immigration(self,im_size,im_dist_table):
        # new immigrants
        time_index=self.member[0].time_index
        n=int(im_size[time_index])
        list_immigrants=([self.setup_immigrant(im_dist_table) for j in range(n)])
        self.member.extend(list_immigrants)
        return list_immigrants

            
    def step(self, model):
        #update age and time_index for all individuals from last year  
        self.member=[ind.step_aging() for ind in self.member]
        #update the population time_index
        self.set_timeindex()
        

        #fertility update    
        self.member=[ind.birth(model.fertility_table) for ind in self.member]
        # count the number of fertile people
        self.women_fertile_actual=[(item.fertile==1) for item in self.member].count(True)
        
        #add new borns
        list_newborn=self.add_newborn()
        
        #adjustment factor
        time_index_temp=int(self.time_index)
        self.set_adjust(model.outmigration_table[time_index_temp],model.em_size[time_index_temp])
        #print(self.time_index, self.adjust_factor)

        
        #summerize information on newborn
        self.number_newborn=np.zeros([2,number_region])
        for i in range(number_region):
            for j in range(2):
                self.number_newborn[j,i]=[(item.sex==j and item.region==i) for item in list_newborn].count(True)

        #add immigrants
        immigrants=self.add_immigration(model.im_size,model.im_dist_table)
        
        # death, outmigration and internal movement
        self.member=[ind.step_other(model, self.adjust_factor) for ind in self.member]
        
        # out migrants
        list_out=[ind for ind in self.member if ind.status==2]
        
        self.out_summary=np.zeros([move_age+1,2,number_region])
        for i in range(len(list_out)):
            ##index0=list_out[i].age // 5
            index0=list_out[i].age
            index1=list_out[i].sex
            index2=list_out[i].region
            self.out_summary[index0,index1,index2] += 1
            
        ## list_move=[ind for ind in self.member if ((ind.region!=ind.region_old) & (ind.region_old!=number_region))]
        list_move=[ind for ind in self.member if ind.status==3]
        ## element i,j denote the number of individuals who move from i to j
        self.move_summary=np.zeros([move_age+1,2,number_region, 2])
        for i in range(len(list_move)):
            index_age=list_move[i].age
            index_sex=list_move[i].sex
            index0=list_move[i].region_old
            index1=list_move[i].region
            ## move out
            self.move_summary[index_age, index_sex,index0,0] += 1 
            self.move_summary[index_age, index_sex,index1,1] += 1        
            
        # death
        list_dead=[ind for ind in self.member if ind.status==1]
        
        self.dead_summary=np.zeros([bins,2,number_region])
        for i in range(len(list_dead)):
            ##index0=list_dead[i].age // 5
            index0=list_dead[i].age 
            index1=list_dead[i].sex
            index2=list_dead[i].region
            self.dead_summary[index0,index1,index2] += 1

        #remove the dead and outmigrated;       
        self.remove_exit()

        
        
    def summarize(self):
        # summerize the output into the three demensional array
        # axis 0: age groups 
        # axis 1: gender
        # axis 2: the region
        # summary
        self.summary=np.zeros([maxage+1,2,number_region])
        self.size=len(self.member)
        self.women_fertile=0
        for i in range(self.size):
            index0=self.member[i].age
            index1=self.member[i].sex
            index2=self.member[i].region
            self.summary[index0,index1,index2] += 1
            if index1==1 and index0>=14 and index0<=48:
                self.women_fertile +=1
            
        self.im_summary=np.zeros([move_age+1,2,number_region])
        im_mask_index=[item.age==item.age_im for item in self.member]
        im_list=list(compress(self.member,im_mask_index))
        for i in range(len(im_list)):
            #index0=im_list[i].age // 5
            index0=im_list[i].age
            index1=im_list[i].sex
            index2=im_list[i].region
            self.im_summary[index0,index1,index2] += 1

             
                
        
        
### the model class

class model(object):
    """ An projection model contains all necessary parameters:
 
    Attributes:
        mortality_table:
        outmigration_table: 
        imigration_table: 
        fertility_table: 
        move_table:
        
    """
    
    def __init__(self, mortality_table=[np.ones((number_region, 2, maxage+1)) for i in range(max_year)], 
                 immigration_table=[np.zeros((number_region))]*max_year, 
                 fertility_table=[np.zeros((number_region,range_fertility)) for i in range(max_year)],
                 outmigration_table=[np.zeros((number_region, 2, move_age+1)) for i in range(max_year)],
                 move_table=[np.zeros((number_region, 2, move_age+1)) for i in range(max_year)],
                 im_dist_table=[np.zeros((2*(move_age+1))) for i in range(max_year)],
                 im_size=np.zeros(max_year),em_size=np.zeros(max_year),
                 mov_mat=[np.zeros((number_region+1,20,number_region)) for i in range(move_max-start_year+1)],
                 table_link_a=np.zeros((2, maxage)), 
                 table_link_r=np.zeros((number_region+1))) :                
                     
        self.mortality_table=mortality_table
        self.outmigration_table=outmigration_table
        self.immigration_table=immigration_table
        self.fertility_table=fertility_table
        self.move_table=move_table
        self.im_dist_table=im_dist_table
        self.im_size=im_size
        self.em_size=em_size
        self.mov_mat=mov_mat
        self.table_link_a=table_link_a
        self.table_link_r=table_link_r
        
    def set_fertility(self, file):
        datafile=path+'/'+file
        data_in=pd.read_csv(datafile) 
        #data_in=FileClient.load_csv_to_pandas(f"{datafile}") 
        #print(data_in)
        for index, row in data_in.iterrows():
            # index_temp starts at zero
            index_temp=int(row.year-start_year)
            # region: 0-355
            r=int(row.region)
            #age starts from 15
            a=int(row.age)-15
            self.fertility_table[index_temp][r,a]=row.prob  
            
    def set_mortality(self, file):
        datafile=path+'/'+file
        data_in=pd.read_csv(datafile)
        #data_in=FileClient.load_csv_to_pandas(f"{datafile}") 
        for index, row in data_in.iterrows():
            index_temp=int(row.year-start_year)
            # region: 1-356
            r=int(row.region)
            # sex=1 or 2
            s=int(row.sex)-1
            #age: from 0 to 119
            #age 120 is set to 1 as default
            a=int(row.age)
            self.mortality_table[index_temp][r,s,a]=float(row.prob)
    
    def set_migration(self, file):
        datafile=path+'/'+file
        data_in=pd.read_csv(datafile)  
        #data_in= FileClient.load_csv_to_pandas(f"{datafile}") 
        #print(data_in)
        for index, row in data_in.iterrows():
            index_temp=int(row.year-start_year)
            # region: 1-366
            r=int(row.region)
            # sex=1 or 2
            s=int(row.sex)-1
            #age start at index
            a=int(row.age)
            #print(row)
            self.outmigration_table[index_temp][r,s,a]=float(row.pr_mig)
            self.move_table[index_temp][r,s,a]=float(row.pr_mov )
    

    def set_immigration_dist(self, file):
        datafile=path+'/'+file
        data_in=pd.read_csv(datafile)
        #data_in= FileClient.load_csv_to_pandas(f"{datafile}") 
        for index, row in data_in.iterrows():
            index_temp=int(row.year-start_year)
            s=int(row.sex)-1
            a=int(row.age)        
            self.im_dist_table[index_temp][s*(move_age+1)+a]=float(row.pr_immigrant)
            
    def set_im_size(self, file):
        datafile=path+'/'+file
        data_in=pd.read_csv(datafile)
        #data_in= FileClient.load_csv_to_pandas(f"{datafile}") 
        for index, row in data_in.iterrows():
            index_temp=int(row.year-start_year)       
            self.im_size[index_temp]=(row.tot_immigrants)
            self.em_size[index_temp]=(row.tot_emigrants)
    
    def set_mov_mat(self, file):
        datafile=path+'/'+file
        data_in=pd.read_csv(datafile)  
        #data_in= FileClient.load_csv_to_pandas(f"{datafile}") 
        #print(data_in)
        for index, row in data_in.iterrows():
            index_temp=int(row.year-start_year)
            s=int(row.agesexgr)-1
            a=int(row.region)
            r=int(row.d_region)
            # a, original region, s age and gender group, r, destination region        
            self.mov_mat[index_temp][a,s,r]=float(row.prob)
            
    def set_link_a(self, file):
        datafile=path+'/'+file
        data_in=pd.read_csv(datafile)
        #data_in= FileClient.load_csv_to_pandas(f"{datafile}") 
        for index, row in data_in.iterrows():
            s=int(row.sex)-1
            a=int(row.age)        
            self.table_link_a[s,a]=int(row.agesexgr-1)    
            
    # def set_link_r(self, file):
        # datafile=path+'/'+file
        # data_in=pd.read_csv(datafile)
        # for index, row in data_in.iterrows():
            # r=int(row.region)        
            # self.table_link_r[r]=int(row.origin_index)
        # # region=356 (number_region) is set to zero by default             

            
    

testmodel=model()

# mortality rate;
testmodel.set_mortality("mortality.csv")

# fertility rate
testmodel.set_fertility("fertility.csv")

# out migration and moving rate;
testmodel.set_migration("migration.csv")

# immigrants age and gender distribution
testmodel.set_immigration_dist("distr_immigration.csv")

# number of immigrants
testmodel.set_im_size("tot_migration.csv")

# internal moving matrix
testmodel.set_mov_mat("mov_mat.csv")

# the link information 
testmodel.set_link_a("link_a.csv")
# testmodel.set_link_r("link_r.csv")

# check the sum of destination probability sum up to 1
print("immigrants: probablity check", testmodel.im_dist_table[0][:].sum())
print("mov_mat: probablity check", testmodel.mov_mat[0][1,1,:].sum())

    

Region_label=["county "+str(i)+" " for i in range(1, number_region+1)]
Region_label.append("nationwide ")


# generate a test base population of size 10000
testpopulation=population()

def setup_individual(r,s,a):
    ind=individual()
    ind.sex=s
    ind.region=r
    ind.age=a
    ind.POB=ind.region
    ind.status=0
    ind.time_index=-1
    return ind


def generate_population(population, file):
    datafile=path+'/'+file
    data_in=pd.read_csv(datafile) 
    #data_in= FileClient.load_csv_to_pandas(f"{datafile}") 
    #print(data_in)
    population.member=[]
    for index, row in data_in.iterrows():
        # region: 0-355
        r=int(row.region)
        s=int(row.sex)-1
        a=int(row.age)

        n=int(row['pop'])
        
        # NOTE: here we must use list comprehension, 
        # cannot use []*n
        subpop=[setup_individual(r,s,a) for i in range(n)]

        population.member.extend(subpop)
    
    population.set_timeindex()
    population.summarize()
        
generate_population(testpopulation, "population_county.csv")
print("initial population generated")


# simulation function based on in_population

def population_sim(list_in):

    sim_index=list_in[0]
    # important to reseed, otherwise will get same outcome
    np.random.seed()
    # simulate the model
    model=testmodel
    # use deepcopy to ensure that all simulation start with the 
    # same baseline population 
    population=copy.deepcopy(list_in[1])
    
    # initilize the output 
    output=[population.summary]
    output_im=[population.im_summary]
    output_n_newborn=[population.number_newborn]
    output_dead=[population.dead_summary]
    output_out=[population.out_summary]
    output_move=[population.move_summary]
    output_fertile=[population.women_fertile]
    output_fertile_actual=[population.women_fertile_actual]
    
    for i in range(number_year):
        population.step(model)
        population.summarize()
        output.append(population.summary)
        output_im.append(population.im_summary)
        output_n_newborn.append(population.number_newborn)
        output_dead.append(population.dead_summary)
        output_out.append(population.out_summary)
        output_move.append(population.move_summary)
        output_fertile.append(population.women_fertile)
        output_fertile_actual.append(population.women_fertile_actual)
       
    res=[output, output_im, output_n_newborn, output_dead, output_out, output_move, output_fertile, output_fertile_actual]

    fs = FileClient.get_gcs_file_system()

    with fs.open(workpath+'/'+'sim_out'+sim_mark+str(sim_index)+'.pkl', mode='wb') as file:
        pickle.dump(res, file, protocol=4)

    return sim_index


