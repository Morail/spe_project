# Simulation and Performance Evaluation project
## Author
**Marco Frassoni - matr. 194513**

## Description
The goal of the project is to implement a Discrete Event Simulation for two different Medium Access Protocol, which are 
respectively **ALOHA** and **CSMA**.
The DES is written in the Python language (Python version 3.9), requirements such as numpy or matplotlib are listed in 
the `requirements.txt` file. following the [PIP convention](https://pip.pypa.io/en/stable/reference/requirements-file-format/) 

The simulator is implemented in an object-oriented model. In order to simplify the model, the time is finite and discrete
such that it evolves with fixed increment. Each increment corresponds to an epoch (see the next paragraph _Configuration_)

## Configuration
Before running a simulation, it is possible to modify the parameters of the model in order to test how these values
affects the output of the simulation.
The parameters to be modified are written into the configuration file **`config.ini`** 
There are several parameters that could be modified in order to affect the executions:
 - **`NumRuns`** the number of simulations to be run
 - **`NumEpochs`** the duration of each simulation expressed in time intervals
 - **`NumStations`** number of devices linked to the single communication channel; different configuration numbers for each simulation run (comma separated values)
 - **`MaxBackoffTime`** indicates the maximum time, expressed in _epochs_, that each station is willing to attend to retransmit a packet that was dropped due to collision before losing this packet.
 - **`Seed`** the Random Number Generator is re-initialized at each simulation; in order to ensure reproducibility is possible to set a seed that would be used to init the RNG instead.
 - **`IsDebug`** if set to `True` it sets the log level to DEBUG, and it prevents plots to be stored on filesystem.  

## Running a simulation
To execute the simulator it is sufficient to run one of the following commands:
 - **`python simulator/simulations.py`** to simulate both ALOHA and CSMA protocols
 - **`python simulator/aloha.py`** to simulate the ALOHA protocol
 - **`python simulator/csma.py`** to simulate the ALOHA protocol

Code is not optimized to be run in parallel. Running a simulation with an important number of runs and stations could 
take up a lot of resources and take quite a while to be completed. To make a comparison, running 20000 simulations 
with 10 stations takes up to 10 minutes on my laptop.

## Simulation results
### Data and statistics
Overall data and statistics obtained from the data analysis of the observation of the simulations are persisted and 
saved into the `data` directory. Every run produces three different file with the same name but having different 
extension; they contain the same data but formatted differently. 

Statistics analysis take into account several different metrics for single simulation configuration. In other words, 
statistics are divided per simulated protocol, per number of stations in the simulation and per each different 
metric under observation, such as for instance throughput and collision rate.

### Plots
The plots produced as an output of each simulation will be saved into the _plots_ directory, only if the `IsDebug` 
configuration in the `config.ini` file is set to False, otherwise plots will be displayed but not saved.