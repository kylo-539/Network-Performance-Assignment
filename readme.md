# Network Performance Assignment - EEN1058

**Author:** Kyle Sheehy   
**Date:** October 2025

## Overview

This repository contains the analysis and simulation files for the Network Performance Assignment. The project analyses WiFi network performance using OMNeT++ simulation data, examining key metrics such as throughput, delay, and packet loss ratio across various scenarios.

## Repository Structure
```

├── QuestionA/ # Question A simulation data
│ ├── DataOfUser1--default-.sca # Default parameters
│ ├── DataOfUser1--1000kbps-.sca
│ ├── DataOfUser1--5000kbps-.sca
│ ├── DataOfUser1--10000kbps-.sca
│ ├── DataOfUser1--15000kbps-.sca
│ ├── DataOfUser1--20000kbps-.sca
│ ├── *.png # Generated visualizations
│ └── QuestionA-Part2.csv # Collated results
│
├── QuestionB-Original-Sim/ # Original sim (connectivity issues after 50m)
│ ├── *.png # Generated visualizations
├── QuestionB-Altered-Sim/ # Adjusted simulations for proper analysis
│ ├── *.png # Generated visualizations
│ └── QuestionB-DistanceAnalysis.csv
│
├── QuestionC/ # WiFi 6 vs WiFi 7 analysis
│ ├── Wifi6/ # WiFi 6 (802.11ax) data files
│ ├── Wifi7/ # WiFi 7 (802.11be) data files
│ ├── QuestionC-WiFi6-vs-WiFi7-Analysis.csv
│ └── *.png # Generated visualizations
│
├── NS3 Fix/ # NS3 installation fixes
│ ├── wifi-example-apps.cc
│ ├── wifi-example-apps.h
│ └── wifi-example-sim-updated.cc
│
├── QuestionA-Part1.py # Question A analysis script (default)
├── QuestionA-Part2.py # Question A analysis script (varying bit rates)
├── QuestionB.py # Question B distance analysis script
├── QuestionC.py # Question C WiFi 6 vs WiFi 7 comparison script
├── readme.txt # Text description of file locations
└── readme.md # This file
```

## Prerequisites

- Python 3.x
- Required Python packages:
  ```bash
  pip install pandas numpy matplotlib
- NS3

# Question A: Network Performance Metrics Analysis
Analyses network performance with varying bit rates

# Part 1 - Default Parameters:
python QuestionA-Part1.py

# Part 2 - Effect of Varying Bit Rates (1,5,10,15,20Mbps)
python QuestionA-Part2.py

## Requirements
QuestionA/ folder must be in the same directory as the scripts

File are named with designated bit rates (e.g. "DataOfUser1-*-1000kbps-.sca")
CSV file provided for alternative Excel analysis

# Question B: Performance Analysis vs Distance
python QuestionB.py

# Important Notes
QuestionB-OriginalSim/: Contains files highlighting connectivity issues after 50m

QuestionB-Altered-Sim/: Contains adjusted files for actual analysis

Must specify in the code which dictionary you want to perform the analysis on

# Question C: WiFi 6 and WiFi 7 Comparison
Comprehensive analysis comparing WiFi 6 (802.11ax) and WiFi 7 (802.11be) performance across:

Distances: 0m, 30m, 60m, 90m, 120m, 150m
User counts: 1, 10, 20, 50 users

python QuestionC.py

# Output
- CSV analysis: QuestionC-WiFi6-vs-WiFi7-Analysis.csv
- Throughput comparison plots
- Delay comparison plots
- Packet Loss Ratio (PLR) comparison plots
- Side-by-side distance comparisons

## Metrics Calculated
All scripts calculate the following key network performance metrics:

- 1. Average Throughput (Kbps):
    Data successfully transmitted per unit time
- 2. Average Delay (ms): 
    Time taken for packets to traverse the network
- 3. Packet Loss Ratio (PLR):
    Proportion of packets lost during transmission

## NS3 Installation Fixes
The NS3-Fix/ folder contains modified files required to resolve installation issues in NS3:

- wifi-example-apps.cc : Application layer modifications
- wifi-example-apps.h : Header file definitions
- wifi-example-sim-updated.cc : Updated simulation parameters

These files were modified and copied into the NS3 environment in Ubuntu during development

## Data Files
All .sca (scalar) files are OMNeT++ simulation results containing:
- TX/RX packet counts
- Delay statistics (in nanoseconds)
- WiFi frame counts
- Delay Metrics (min, max, average, count)

File naming convention:
"DataOfUser1-[timestamp]-[distance]-[users]-[WiFiType]-[run].sca"

## Visualisations
Each question generates comprehensive visualisations:

Question A: Bit rate, throughput, delay, and PLR plots
Question B: Distance vs performance metrics
Question C: WiFi 6 vs WiFi 7 comparative analysis with side-by-side bar charts

All plots are saved as high-resolution PNG files.

## Author
Kyle Sheehy

## License
This project is submitted as part of academic coursework for DCU.