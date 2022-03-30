


import importlib
import sim_aux
import copy
import multiprocessing as mp
import time
import sim_para
import pickle
import os



#Using multiprocessing
if __name__ == "__main__":
    
    def set_nicesness():
        niceness=os.nice(0)
        os.nice(5-niceness)
    
    pool = mp.Pool(sim_para.number_core, initializer=set_nicesness)
    
    print('number of cores used: ', sim_para.number_core)
    print('number of simulations to be performed: ', sim_para.number_loop)
    print('number of years to be porjected: ', sim_para.number_year) 
    start_time=time.time()
    
    list_pop=[[i,sim_aux.testpopulation] for i in range(sim_aux.number_loop)]
    
    print('Starting simulation..')

#    res=pool.map(sim_aux.population_sim, list_pop)
    res_temp=pool.imap(sim_aux.population_sim, list_pop)
    
    res=[]
    count=0
    for x in res_temp:
        count=count+1
        if count%sim_para.number_core == 0:
            print('finished ', count, "out of ", sim_para.number_loop, " time  used --- %s seconds ---" % (time.time() - start_time))
        
    print("total time  used --- %s seconds ---" % (time.time() - start_time))
  
    #print('number of newborns: year 0 to 5')
    #print('first simulation')
    #print(res[0][2][0][1,40]) 
    #print(res[0][2][1][1,40]) 
    #print(res[0][2][2][1,40]) 
    #print(res[0][2][3][1,40]) 
    #print(res[0][2][4][1,40]) 
    ##print('last simulation')
    ##print(res[-1][2][0][1,-5:]) 
    ##print(res[-1][2][1][1,-5:]) 
    ##print(res[-1][2][2][1,-5:]) 
    ##print(res[-1][2][3][1,-5:]) 
    ##print(res[-1][2][4][1,-5:]) 
 
    #print('death year 0 to 5')
    #print('first simulation')
    #print(res[0][3][0][:,:,40].sum()) 
    #print(res[0][3][1][:,:,40].sum()) 
    #print(res[0][3][2][:,:,40].sum()) 
    #print(res[0][3][3][:,:,40].sum()) 
    #print(res[0][3][4][:,:,40].sum()) 
 
    #print('out-migration year 0 to 5')
    #print('first simulation')
    #print(res[0][4][0][:,:,40].sum()) 
    #print(res[0][4][1][:,:,40].sum()) 
    #print(res[0][4][2][:,:,40].sum()) 
    #print(res[0][4][3][:,:,40].sum()) 
    #print(res[0][4][4][:,:,40].sum()) 

    #print('immigration year 0 to 5')
    #print('first simulation')
    #print(res[0][1][0][:,:,40].sum()) 
    #print(res[0][1][1][:,:,40].sum()) 
    #print(res[0][1][2][:,:,40].sum()) 
    #print(res[0][1][3][:,:,40].sum()) 
    #print(res[0][1][4][:,:,40].sum())     
    
    #print('population size year 0 to 5')
    #print('first simulation')
    #print(res[0][0][0][:,:,40].sum()) 
    #print(res[0][0][1][:,:,40].sum()) 
    #print(res[0][0][2][:,:,40].sum()) 
    #print(res[0][0][3][:,:,40].sum()) 
    #print(res[0][0][4][:,:,40].sum()) 
    

    ## save the simulation results to a pkl file
    
    # file=open(sim_aux.path+'/'+'sim_out'+sim_para.run_index+'.pkl', 'wb')
    
    # pickle.dump(res, file)
    
    # file.close()

    ## data is too big to pickle, so clean up here and save to csv files instead
    
    
    # region_selection=[0, 22, 122, 227, 356]
    # region_name=['Oslo','Utsira', 'Eidsvoll',  'Bygland', 'Nationwide']

    # Region_label=["county "+str(i)+" " for i in range(1, number_region+1)]
    # Region_label[122]='Eidsvoll'  
    # Region_label[0]='Oslo'  
    # Region_label[22]='Utsira'
    # Region_label[227]='Bygland'  
    # Region_label.append("nationwide ")
    
    # number_loop=len(res)
    # print('simulation is done, performed simulation number ',number_loop)
    # number_year=len(res[0][0])-1
    # print("simulate %s years" % number_year)
    
    # sim_size_full=[]
    # sim_im=[]
    # sim_newborn=[]
    # sim_dead=[]
    # sim_out=[]
    # sim_move=[]

    # for i in range(len(res)):
        # sim_size_full.append(res[i][0])
        # sim_im.append(res[i][1])
        # sim_newborn.append(res[i][2])
        # sim_dead.append(res[i][3]) 
        # sim_out.append(res[i][4]) 
        # sim_move.append(res[i][5]) 

    # res_sim_size_full=np.sum(sim_size_full,0)/number_loop

    # #   Population size by one-year age intervals, sex, municipality and year 
    # #  simyear+1, age, gender, region


    # # make the array into a dataframe, where there are (number_year+1)*121*2*356 lines
    # # where columns are 'year_projection', 'age', 'gender', 'region', 'population'

    # lines=(number_year+1)*121*2*356

    # c=0
    # sim_output=np.zeros([lines,5])
    # for i in range(number_year+1):
        # for j in range(120):
            # for k in range(2):
                # for l in range(356):
                    # sim_output[c,0]=i
                    # sim_output[c,1]=j
                    # sim_output[c,2]=k
                    # sim_output[c,3]=l
                    # sim_output[c,4]=res_sim_size_full[i,j,k,l]
                    # c += 1
    # df_sim_size=pd.DataFrame(sim_output)
    # df_sim_size.columns=['year_projection', 'age', 'gender', 'region', 'population']

    # # look at the projection for year 15 (year=0 is the base year)
    # df_sim_size[df_sim_size['year_projection']==2].head()


    # df_sim_size[df_sim_size['age']==120].sum()

    # # ## get the knr variable into the dataframe 
    # # and save to output file

    # datafile=path+'/'+'population.csv'
    # data_population=pd.read_csv(datafile)

    # a=data_population['knr'].unique()
    # a.sort()

    # df_knr=pd.DataFrame(a)

    # df_knr.reset_index(inplace=True)

    # df_knr.head()

    # df_knr.columns=['region', 'knr' ]

    # print(df_knr.head())

    # ## merge the region variable in

    # df_pop=df_sim_size.merge(df_knr, on='region')

    # df_pop.drop(columns=['region'], inplace=True)

    # # df_pop[(df_pop['year_projection']==15) & (df_pop['age']==55)].tail()

    # df_pop.to_csv(path+'/'+'population_sim.csv', index=False)


    # ## check cohort 
    # df_pop['year']=df_pop['year_projection']+2020
    # df_pop['cohort']=df_pop['year']-df_pop['age']

    # df_oslo=df_pop[(df_pop['knr']==301) & (df_pop['cohort']==2010)].groupby('age', as_index=False).sum()
    # df_oslo.head()

    # # plot the number of the 2010 cohort at Oslo

    # plt.figure(figsize=(13,10), dpi= 80)
    # plt.plot(df_oslo['age'], df_oslo['population'], '-', color='gray')
    # plt.show()



    # # Components by municipality and year (6outcomes x 356munic x 30years)
    # # - Births
    # # - Deaths
    # # - Immigrations
    # # - Emigrations
    # # - In-migrations (domestic)
    # # - Out-migration (domestic)
    # # 



    # ## imput the size of emigrants and out-emigrants

    # # average over simulations

    # res_sim_im=np.sum(sim_im,0)/number_loop
    # res_sim_newborn=np.sum(sim_newborn,0)/number_loop
    # res_sim_dead=np.sum(sim_dead,0)/number_loop
    # res_sim_out=np.sum(sim_out,0)/number_loop
    # res_sim_move=np.sum(sim_move,0)/number_loop 


    # lines=(number_year+1)*121*2*356

    # c=0
    # sim_out_2=np.zeros([lines,10])

    # for i in range(number_year+1):
        # for j in range(120):
            # for k in range(2):
                # for l in range(356):
                    # sim_out_2[c,0]=i
                    # sim_out_2[c,1]=j
                    # sim_out_2[c,2]=k
                    # sim_out_2[c,3]=l
                    # sim_out_2[c,4]=res_sim_im[i,j,k,l]
                    # sim_out_2[c,5]=res_sim_newborn[i,k,l]
                    # sim_out_2[c,6]=res_sim_dead[i,j,k,l]
                    # sim_out_2[c,7]=res_sim_out[i,j,k,l]
                    # sim_out_2[c,8]=np.sum(res_sim_move[i,j,k,l,:])
                    # sim_out_2[c,9]=np.sum(res_sim_move[i,j,k,:,l])
                    # c += 1
    # df_sim_size_2=pd.DataFrame(sim_out_2)
    # df_sim_size_2.columns=['year_projection', 'age', 'sex', 'region', 'immigrants', 'births', 'deaths', 'outmigrants', 'move_out', 'move_in']


    # df_pop=df_sim_size_2.merge(df_knr, on='region')

    # df_pop.drop(columns=['region'], inplace=True)

    # # check consistency between move in/out
    # print(df_pop[df_pop['year_projection']==1]['move_out'].sum())
    # print(df_pop[df_pop['year_projection']==1]['move_in'].sum())

    # df_pop.to_csv(path+'/'+'components_sim.csv', index=False)


    
