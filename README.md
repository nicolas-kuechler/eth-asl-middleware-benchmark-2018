# Advanced Systems Lab - Autumn Semester 2018

## Repository Overview

| Component              | Location            |
| ---------------------- | ------------------- |
| Middleware Code        | /java               |
| Experimental Setup     | /python/experiments |
| Data Analysis          | /python/analysis    |
| Report                 | /report             |


## Data
The report is based on the data in the archive data.zip

The top-level folder structure of the data matches the structure of the report
(i.e. exp21 corresponds to section 2.1 Baseline without Middleware - One Server).
Each set of experiments is divided into folders for the different evaluated configurations.
The folder of each experiment is partitioned further into folders for the repetitions and files containing the aggregated data from client and middleware in a csv format.

The file mongodump.zip contains an export of the experiment database based on the files in data.zip


#### Example
```
\data\exp31\read_only\w_32\vc_8\rep_0
```
This folder contains the data of the first repetition of the experiment with 8 virtual clients and 32 worker-threads in the read-only workload in the system setup of section 3.1 Baseline with Middleware - One Middleware

#### Data Files

| File                   | Description |
| ---------------------- | -------- |
| processed_mw.log       | aggregated data collected from the middleware over multiple repetitions (csv format) |
| processed_client.log   | aggregated data collected from the client over multiple repetitions (csv format)  |
| client_XX.log          | memtier_benchmark log data for a single experiment. The first $`X \in [0,1,2]`$ indicates the client VM  and the second $`X \in [0,1]`$ stands for the instance on the VM. (json format)|
| mw_out_0X.log          | general output of the middleware $`X \in [0, 1]`$ for a single experiment (standard)|
| mw_stat_0X.log         | statistics of the middleware $`X \in [0, 1]`$ for a single experiment (whitespace separated according to header) |


## Middleware

### Prerequisites
- ant
- java 1.8

### Build

The middleware software is built using ant:
```
ant -buildfile java/build.xml
```

This results in a jar file located in:
```
\java\dist\middleware-kunicola.jar
```

### Running

```
 java -jar ./java/dist/middleware-kunicola.jar -l localhost -p 6379 -t 10 -s false -m localhost:11211
```

## Experiment Simulation and Data Analysis

### Prerequisites
- conda environment asl.yml
- MongoDB
- octave (for queuing models)

### Running
Running experiment_suite.py will launch experiments according to the json configurations in python/experiments/configs.
General configurations including the settings of the Azure cloud environment are done in python/experiments/configs/config.py

```
 python experiment_suite.py -id simulation -exp exp21 exp22 exp31 exp32 exp41 exp51 exp52 exp60 -vmstart initial
 ```

The jupyter notebooks in python/analysis include the data analysis for each section of the report.

## Author

* **Nicolas Küchler** -  Legi: 14-712-129
