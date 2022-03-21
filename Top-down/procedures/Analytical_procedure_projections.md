# OBJECTIVE

The script performs collection of climate indices related to hydrometeorological hazards.
The spatial information is collected from [WB CCKP](https://climateknowledgeportal.worldbank.org/download-data).

The climate component estimates the mean or max anomaly over the reference baseline for a selection of hazard-related climate indices for a specified time horizon under 3 RCPs (2.6, 4.5, 8.5).

The output is:
- presented as map and dynamic chart at each model run
- exported in form of tables, statistics, charts (excel format) and maps (geopackage) at each model run


# SCRIPT OVERVIEW

- Script runs on one country at time and for a specific set of indices (depending on hazard selected) to keep the calculation time manageable
- User input defines country and settings
- Settings affect which input data is selected, how the processing runs (criteria), and how the results are presented
- All RCP scenarios are always considered and presented in the results: RCP 2.6, 4.5, 8.5
- The estimate is provided for median, 10th-percentile and 90th percentile
- The information is aggregated at ADM2 level and presented dynamically
- The results are exported as csv (table) and geopackage (vector)


# SCRIPT STRUCTURE

- SETUP: environment and libraries
- USER INPUT: required
- SETTINGS: default parameters can be changed by user
- DATA MANAGEMENT: global datasets are loaded according to user input
- DATA PROCESSING: datasets are processed according to settings
- PREVIEW RESULTS: plot tables and maps
- EXPORT RESULTS: results are exported as gpkg and csv according to templates


# PRE-PROCESSED CLIMATE INDICES

Climate data processing from CDS (or others)

**Version:** CMIP6 – GCM 

**Ensemble:** the largest number of models available for the required dimensions. 

Each index is stored as multi-dimensional netcdf. 

**Dimensions:** 
   - **RCP:** 2.6, 4.5, 8.5 
   - **Period:** {Historical}, [2040, 2060, 2080] - or decadal? 
   - **Ensemble range (percentile):** 10, 50, 90 
   - **Metric:** {Mean, SD}, [Mean] 

# PRE-REQUISITES (OFFLINE)

- Anaconda and python installed > Possibly we move to jupyter desktop Autoinstaller
- Create environment from ccdr_analytics.yml

# SCRIPT STEP-BY-STEP

## SETUP

- Load required libraries

## USER INPUT

- Hazard of interest: Flood and Landslide, Tropical Cyclone, Coastal flood, Drought and Water Scarcity, Heat
- Country of interest (1): Name dropdown (link ISOa3 value) 
- Time horizon: 2040, 2060, 2080, 2100

## SETTINGS (DEFAULT can be changed)

- Criteria for value aggregation: a) MAX; b) Mean

------------------------------------------

## DATA MANAGEMENT

- Creation of string request based on input (hazard, country and period)
- String links to nc files hosted / downloaded from CCKP

## DATA PROCESSING - PROJECTIONS

- Run zonal statistic using ADM2 as zone and nc data as value based on input (country, horizon, RCP) and settings aggregation criteria

|          Hazard           |               Associated climate indices           |
|---------------------------|----------------------------------------------------|
| River floods / Landslides |     Days with rainfall > 10 mm [days]              |
|                           |     Maximum 5-day precipitation [mm]               |
|                           |     Very wet day precipitation [days/month]        |
|     Wet landslides        |     Days with rainfall > 10 mm [days]              |
|     Coastal floods        |     Mean Sea Level Rise [m]                        |
|     Tropical cyclone      |     Number of days with strong winds [days]        |
|                           |     Daily maximum 10-m wind speed [m/s]            |
|     Agricultural drought  |     Standard Precipitation-ET Index (SPEI) [-]     |
|     Heat stress           |     Heat index [°C]                                |
|     Wildfire?             |     Standard Precipitation-ET Index (SPEI) [-]     |
|                           |     Heat index                                     |


## PREVIEW RESULTS - PROJECTIONS

- Plot indices as map and as tables/charts
  - On ADM2 map selection (mouse click), each indices is plotted as a one line chart that includes:
    -  3 lines of different colors (green, yellow, orange) representing the median for each RCP
    -  3 shade areas representing the related p10 and p90 for each RCP
    -  X is period (as from input)
    -  Y is intensity (depends on index selection)
    -  Title specify aggregation criteria

Similar to common RPC representation:

<img width="500" src="https://user-images.githubusercontent.com/44863827/154677308-610702d4-1312-4ce5-b16c-e2b99e961c1e.png">

## EXPORT RESULTS - PROJECTIONS

- Export output as gpkg and csv
