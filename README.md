# Simulation and Performance Evaluation project
## Author
**Marco Frassoni matr. 194513**

## Description
The goal of the project is to implement a Discrete Event Simulation for two different Medium Access Protocol, which are 
ALOHA and CSMA.
The DES is written in the Python language (Python version 3.9), requirements such as numpy or matplotlib are listed in 
the _requirements.txt` file. following the PIP convention. 
The simulator is implemented in an object-oriented model.

## Usage
Before running the simulation the configuration file config.ini should be modified, setting the desired parameters for
the executions, such as for example the number of simulations to be run, the number of epochs, ... 

To execute the simulator it is sufficient to run one of the following commands:
 - **`python simulator/simulations.py`** to simulate both ALOHA and CSMA protocols
 - **`python simulator/aloha.py`** to simulate the ALOHA protocol
 - **`python simulator/csma.py`** to simulate the ALOHA protocol

The output of each simulation will be saved into the _plots_ directory if the `IsDebug` configuration in the config.ini 
file is set to False, otherwise plots will be displayed but not saved. 
