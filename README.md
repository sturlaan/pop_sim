# A dynamic spatial microsimulation model for population projections

This project documents a dynamic spatial microsimulation model for regional population projections. This model is developed by researchers at Statistics Norway for research purposes. The model is set up for projecting the population size and composition of Norwegian municipalities, but can easily be adapted for other geographies.

# Model

## Indiviudal and Population

The underlying spatial dynamic discrete-time microsimulation model
simulates individual demographic events. The demographic and
geographical characteristics of each individual are tracked over their life span. 

In our current model, the unit of simulation in individual. Household formation and dissolution are not
modeled.

The population is represented by a collection of individuals. The
population at the end of time period \(t-1\) serves as the baseline
population for time period \(t\).

## Life events

The occurrence of a life event at any given discrete time is determined
stochastically by transition probabilities. The life events modelled are:

  - Aging: Deterministic for all individual present at the end of the year

  - Mortality: Based on age- and sex-specific mortality rates for each region

  - Birth: Based on age-specific fertility rates for the females in each region

  - Domestic migration (between municipalities): 
    1. Out-migration: Based on age- and sex-specific out-migration rates for each region. 
    2. In-migration: The destination probabilities of the domestic migrants are assigned depending on age, sex and region of departure (moving matrix).

  - International migration (between municipalities): 
    1. Emigration: Based on age- and sex-specific emigration rates for each region. 
    2. Immigration: The destination probabilities of the immigrants are assigned depending on age and sex.

## Timing of events 

During time period t, we simulate life events for all individuals in
the baseline population. The sequence of the events are the following:

  - Update age and time index. Increasing the age and time index by one effectivly updates the end-of-year population from period t-1 to start-of-year population for period t (age defined as end-of-year age). This is the baseline population of year t. (Note that the time index of the first year of projection is set to 0, as python array indexes start with 0.)

  - Simulate the fertility events of all women and add newborns to the same region as their mothers.

  - Calculate the adjustment factor for emigration, so that the number
    of outmigrants are the same, in expectation, as the model assumptions.

  - Death, emigration and internal out-migration are simulated
    simultaneously for the individuals in the baseline population, including the newborns.

      ”*we assume that mortality, emigration and moving is
      multinomially distributed. This means that after the number of
      births are drawn, we can draw one uniform random variable (X) which
      determines all the outcomes simultaneously. If 0\<X\<pr\_mort then
      the individual dies, if pr\_mort\<X\<(pr\_mort+pr\_emig) then the
      individual emigrates, if (pr\_mort+pr\_emig)\<X\<(pr\_mort+pr\_emig+pr\_mov) then the
      individual moves, and if (pr\_mort+pr\_emig+pr\_mov)\<X\<1 then
      nothing happens to the individual. This should produce the same
      expected number of events as the CC model since we ensure that only
      one event can happen to each individual and that all events use the
      same start-of-year population.* ”

  - Simulate and assign region destinations for immigrants and domestic movers according age, sex and origin

  - Remove individuals that die or emigrate

The resulting population will serve as the baseline population for
period \(t+1\).

# Python implementation

The python code can be found at \~/Population. Best to run on
sl\_stata\_p3 (most powerful?). Command line: `python3.6 sim_main.py`

## Orgnizations

The work is divided into three parts:

1.  data preparison
    
    1.  Data\_check\_oct\_2022.ipynb

2.  simulatoin
    
    1.  sim\_main.py: The code to call up the aux file and parameter
        files to run the simulation
    
    2.  sim\_para.py: script where the parameters are set
    
    3.  sim\_aux.py: script where the main simulation procedures are
        defined.

3.  results collection and reporting
    
    1.  result\_collection\_oct2022.ipynb

### Note on parallel computation: 

The microsimulation takes time. To reduce the running time, we have used
the multiprocessing package in python to enable parallel implementation.
Note that we have also set the nice value to 5 (using the initalizer
function), and reset the seed in each child process otherwise we end up
with identical draws.

## Parameters and input

### Parameters to be set

|              |                                             |
| :----------: | :-----------------------------------------: |
| number\_loop |            Number of simulations            |
| number\_year |             Years of projection             |
| number\_core | Number of cores used (parallel compuations) |
|  sim\_mark   | Suffix to output files sim\_out”sim\_mark”  |

### Variables that are hard coded in the script

|                  |                                                                               |                      |
| :--------------: | :---------------------------------------------------------------------------: | :------------------: |
|       path       |                  Folder where the input and output data lies                  | `~/Population/g2020` |
|  number\_region  |                           number of unique regions                            |         356          |
|      maxage      | maximum age (during the year, but there is no one at this age as of 31st dec) |         120          |
| range\_fertility |                                                                               |        15-49         |
|    max\_year     |                          maximum years of projection                          |          31          |
|    base\_year    |           the year when the base data comes from (as of 31st, dec)            |         2019         |
|    move\_age     |       maximum age for those who are allowed to migrate (within and out)       |          69          |

### Input data for projection:

the raw data can be found at ` $REGFRAM/sim/wk48/g2020.  `They are then
transferred to the working path defined above.

#### Base population:

population.county.csv: Number of individuals by gender, age and region.

#### Fertility rate:

fertility.csv: probablity of giving birth by age (15-49) and region and
year(2020-2050)

#### mortality rate:

fertility.csv: probablity of giving birth by age (15-49) and region and
year(2020-2050)

#### Outmigration and moving (within country) rate:

migration.csv: probabilities by gender, age and region.

#### immigrants age and gender distribution:

distr\_immigration.csv: probablity distribution of immigrants’ age
(0-69) and gender

#### number of immigrants(outmigrants):

tot\_migration.csv. Note that we don’t usae nubmer of outmigrants listed
here. The actual number is decided via random draws based on
outmigration rate.

#### moving matrix and link information:

mov\_mat\_new.csv, link\_a.csv and link\_r.csv

To reduce the moving matrix size, the individuals have been put into 20
(agesexgroup)<span>\*</span>20 (19 regions + immigrants) cells. The
conditional probablities moving to each region in each cell is then
given. Thus, the mov\_mat matrix is
(20<span>\*</span>20<span>\*</span>number\_region).

## Classes

Three classes are defined.

Individual: individual with properties

Attributes:

  - age: sex: <span>\[</span>0,1<span>\]</span>

  - Region: 356 different regions (kommune in norway)

  - POB: place of birth <span>\[</span>0,1,...,356<span>\]</span> 356:
    foreign born

  - age\_im: age of immigration, native -1

  - status\_birth: <span>\[</span>0,1<span>\]</span>

  - status <span>\[</span>0,1,2,3,4<span>\]</span> 0:normal, 1, dead, 2
    out-migrated, 3, mover within country, 4 immigrant.

  - time\_index

### population, a set(list) of individuals at a given time: 

Attributes:

  - member: a list of indiviudals size: number of individuals in this
    population

  - size: population size

  - summary: 3 dimensional array
    (24<span>\*</span>2<span>\*</span>number\_region) which contains the
    summary information out individuals
    
      - \# axis 0: age groups (in 5 years interval)
    
      - \# axis 1: gender
    
      - \# axis 2: the region

  - im\_summary: similar to summary, but keep track of immigrants

  - dead\_summary: similar to summary

  - out\_summary: similar to summary

  - number\_newborn: 2-d array (2<span>\*</span>number\_region) number
    of newborns for each region.

  - adjust\_factor: The adjust factor for emigration rates (email
    10.03.2021)

### model : An projection model contains all necessary parameters:

Attributes:

  - fertility\_table: probability of giving birth {year specific 2-d
    array on region/age}

  - mortality\_table: probability of mortality {year specific 3-d array
    on region/sex/age}

  - outmigration\_table: probability of moving out of country { year
    specific 3-d array on region/sex/age}

  - move\_table: probability of moving internally {year specific 3-d
    array on region/sex/age}

  - im\_dist\_table: year specific, 2-d array on sex/age

  - im\_size: number of immigramnts {1-d array dimension (max\_year+1)
    <span>\[</span>0,...,30<span>\]</span>}

  - mov\_mat: destination probability { year specific 3-d array
    (agesexgr, orgin\_index, region) }

  - table\_link\_a: agesexgr given age and sex (2-d array )

  - table\_link\_r: orgin\_index given region {1-d array dimension
    (356+1)}
    
      - kommune
        knr-\>region<span>\[</span>0,...,355<span>\]</span>-\>origin\_index<span>\[</span>1,...,19<span>\]</span>-\>
        origingr <span>\[</span>fylk nr?<span>\]</span>
    
      - foreign born region <span>\[</span>356<span>\]</span>
        -\>origin\_index <span>\[</span>0<span>\]</span> -\> origingr
        <span>\[</span>0<span>\]</span>

## Baseline population 

Done by function `generate_population(population, file`. Note that we
should use list comprehension instead of \(\times n\) method to generate
list of individuals with same characteristics.

# Output and result collection

## Results presentation 

### List of out-variables for municipalities:

  - Number of people (total, and separately by sex & age)

  - Number of children born (total, and separately by sex & age)

  - Number of deaths (total, and separately by sex & age)

  - Net migration – difference between in and out moves (total, and
    separately by sex & age)
    
      - We don’t report directly this, but this can be recovered by
        using the following relationship:

pop at \(t\)+1 pop at \(t\)(net change of population)= immigrarnts
outmigrant (net international migration)+ births deaths (net natual
change)+ immigrarnts outmigrant (net national migration)

### Summary stats:

For these out-variables we need the following summary statistics over
all simulations for the nation, the counties and the municipalities
(separately for each year): Mean, sd, max, p80, median, p20, min. For
some reason demographers usually use 20th and 80th percentile as
low/high alternatives.

### Convergence:

Evaluate how different summaries converge when the number of simulations
increase. One suggestion is to present the evolution of mean variable
with CI as a graph with number of simulations on the x-axis. This should
make it easy to see if small municipalities converge slower than large
municipalities.

  - Total population at year 25 (mean & ci)

  - Population of Oslo at year 25 (mean & ci)

  - Population of median sized municipality at year 25 (mean & ci)

  - Population of small sized municipality at year 25 (mean & ci)

  - Nr children in Oslo at year 25 (mean & ci)

  - Nr children in median sized municipality at year 25 (mean & ci)

  - Nr children in small sized municipality at year 25 (mean & ci)

### Population pyramid

Done using `Pyramid_plot(datain,region,brange=200000, indx=0, dpi=90)`

### Year 0, Nationwide

### ear 25, Nationwide

### Year 0, Bygland

### Year 25, Bygland

### Time trend

### Convergence plot

### Year 10, Oslo, all residents

### Year 10, Bygland, all residents 

### Year 25, Bygland, age 10-14, female

### Year 25, Bygland, 80-84, female

#### Year 25, Bygland, 90-94, male

# Results and Discussion
