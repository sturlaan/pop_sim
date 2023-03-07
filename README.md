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

The resulting population is the end-of-year population of period t. The projection is further extended by one period by repeating this procedure for the next period (t+1).

# Python implementation

The python code can be found at https://github.com/statisticsnorway/pop_sim. Command line: `python3.6 sim_main.py`

## Orgnizations

The work is divided into three parts:

1.  Data preparison
    
    1.  Data\_check\_oct\_2022.ipynb

2.  Simulation
    
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
|       path       |                  Folder where the input and output data lies                  | `~/Population/g2022` |
|  number\_region  |                           number of unique regions                            |         356          |
|      maxage      | maximum age (during the year, but there is no one at this age as of 31st dec) |         120          |
| range\_fertility |                                                                               |        15-49         |
|    max\_year     |                          maximum years of projection                          |          31          |
|    base\_year    |           the year when the base data comes from (as of 31st, dec)            |         2019         |
|    move\_age     |       maximum age for those who are allowed to migrate (within and out)       |          69          |

### Input data for projection:

The raw data employed in the analysis are drawn from Norwegian administrative registers.
Researchers can gain access to the data by submitting a written application to the data
owners. Applications must be certified by The Norwegian Data Inspectorate in order
to ensure that data are processed in a manner that protects the personal integrity of
individuals surveyed. Conditional on this approval, Statistics Norway will then determine
which data one may obtain in accordance with the research plan. Inquiries about access to
data from Statistics Norway should be addressed to: mikrodata@ssb.no. More information
is available at: https://www.ssb.no/en/omssb/tjenester-og-verktoy/data-til-forskning


#### Base population:

population.csv: Number of individuals by gender, age and region.

#### Fertility rates:

fertility.csv: probablity of giving birth by age (15-49), region and
year(2022-2050)

#### Mortality rates:

mortality.csv: probablity of dying by age, gender, region and year(2022-2050)

#### Outmigration and internal moving rates:

migration.csv: probabilities for emigrating and moving to other regions by gender, age, region and year.

#### Immigrants age and gender distribution:

distr\_immigration.csv: probablity distribution of immigrants’ age
(0-69) and gender

#### Target number of immigrants and outmigrants:

tot\_migration.csv. Note that we don’t usae nubmer of outmigrants listed
here. The actual number is decided via random draws based on
outmigration rate.

#### Moving matrix and link information:

mov\_mat\_new.csv, link\_a.csv and link\_r.csv

To reduce the moving matrix size, the individuals have been put into 20
(agesexgroup)<span>\*</span>20 (19 regions + immigrants) cells. The
conditional probablities moving to each region in each cell is then
given. Thus, the mov\_mat matrix is (20<span>\*</span>20<span>\*</span>number\_region).

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
    
    
### Summary statistics:

For these out-variables we need the following summary statistics over
all simulations for the nation, the counties and the municipalities
(separately for each year): Mean, sd, max, p80, median, p20, min. For
some reason demographers usually use 20th and 80th percentile as
low/high alternatives.



