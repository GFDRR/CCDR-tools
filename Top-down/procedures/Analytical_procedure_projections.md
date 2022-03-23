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

Climate data processing from CDS

**Version:** CMIP6 – GCM - 

  - CMIP6 – [GCM projections](https://cds.climate.copernicus.eu/cdsapp#!/dataset/projections-cmip6)
    - pro: full selection of variables
    - con: low resolution

  - CMIP6 derived [Climate Extreme Indices](https://cds.climate.copernicus.eu/cdsapp#!/dataset/sis-extreme-indices-cmip6)
    - pro: disaggregated heat indices, better res;
    - con: does not include Wind, SLR, SPEI

**Ensemble:** the largest number of models available for the required dimensions. 

Each index is stored as multi-dimensional netcdf. 

**Dimensions:** 
   - **RCP:** 2.6, 4.5, 8.5
   - **Ensemble member:** r1i1p1f1 
   - **Ensemble range (percentile):** 10, 50, 90
   - **Period:** {Historical (1981-2010)}, [Near term (2021-2040), Medium term (2041-2060), Long term (2081-2100)]
   - **Time scale:** Annual (R10mm, CWD, slr, SPEI); Monthly (Rxday, R99p, tmean); Daily (Heat) 
   - **Metric:** {Mean, Median, P10 P90, SD}, [Mean. Median, P10, P90,] 


|   Name   |                  Description                  |     Source      | Time-scale  |
|:--------:|:---------------------------------------------:|:---------------:|:-----------:|
| R10mm    | Days with rainfall > 10 mm [days]             | CMIP6 Extremes  |   Annual    |
| Rx5day   | Maximum 5-day precipitation [mm]              | CMIP6 Extremes  |   Monthly   |
| R99p     | Extremely wet day precipitation [days/month]  | CMIP6 Extremes  |   Monthly   |
| CWD      | Consecutive Wet Days [days/month]             | CMIP6 Extremes  |   Annual    |
| slr      | Sea Level Rise [m]                            | CMIP6/NASA      |   Annual    |
| sfcWind  | Daily maximum 10-m wind speed                 | CMIP6           |   Annual    |
|          | Number of days with strong winds [days]       | CMIP6           |   Monthly   |
| SPEI     | Standard Precipitation-ET Index [-]           | CMIP6           |   Annual    |
| Heat     | WBGT or UTCI [°C] - bias adjusted             | CMIP6 Extremes  |    Daily    |
| tmean    | Mean surface temperature [°C]                 | CMIP6           |   Monthly   |


# PRE-REQUISITES (OFFLINE)

- Anaconda and python installed > Possibly we move to jupyter desktop Autoinstaller
- Create environment from ccdr_analytics.yml

# SCRIPT STEP-BY-STEP

## SETUP

- Load required libraries

## USER INPUT

- Hazard of interest:
  - Flood and Landslide
  - Drought and Water Scarcity
  - Heat stress
  - Tropical Cyclone
  - Coastal flood

- Country of interest (1): Name dropdown (link ISOa3 value) 

- Time period:
  - Near term (2021-2040)
  - Medium term (2041-2060)
  - Long term (2081-2100)

- Plot (multiple selection):
  - [ ] Historical Mean and SD
  - [ ] Projected Mean and SD (time period)
  - [ ] Mean Anomaly
  - [ ] Normalised Mean Anomaly
  - [ ] Percentile 90th
  - [ ] Percentile 99th

------------------------------------------

## DATA MANAGEMENT

- Online data harvesting does not provide all the variables we want, then he aggregated (mean) layers are pre-calculated for each index and saved as nc for the tool to load and extract zonal statistics.

## DATA PROCESSING - PROJECTIONS

- Compute the required statistics based on the collection of geotiff representing the different combinations of RCP and periods.
- Run zonal statistic using ADM2 as zone and nc data as value based on input (country, period, RCP) and settings aggregation criteria

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
    -  Y is intensity (ramge depends on index and metric selection)
    -  Title specify aggregation criteria

Similar to common RPC representation:

<img width="500" src="https://user-images.githubusercontent.com/44863827/154677308-610702d4-1312-4ce5-b16c-e2b99e961c1e.png">

## EXPORT RESULTS - PROJECTIONS

- Export output as gpkg and csv

<hr>

# EXAMPLE OUTPUT PAKISTAN

## Historical Mean and SD

**R10mm**

<table>
  <tr><td>Mean</td><td>Standard Deviation</td></tr>
  <tr><td><img width=300 src="https://user-images.githubusercontent.com/44863827/159758502-5fa40db8-a2ab-498f-9339-e09f22808445.png"></td><td><img width=300 src="https://user-images.githubusercontent.com/44863827/159758595-72989fc4-ebc5-4ecd-b1c9-5391121a6fde.png"></td></tr>
  <tr><td>CountryMap- ADM 1 mean values</td><td>CountryMap- ADM 1 mean values</td></tr>
</table>

## Projected Mean and SD (time period)

**CWD, SSP 126, Medium term**

<table>
  <tr><td>Mean</td><td>Standard Deviation</td></tr>
  <tr><td><img width=300 src="https://user-images.githubusercontent.com/44863827/159758502-5fa40db8-a2ab-498f-9339-e09f22808445.png"></td><td><img width=300 src="https://user-images.githubusercontent.com/44863827/159758595-72989fc4-ebc5-4ecd-b1c9-5391121a6fde.png"></td></tr>
  <tr><td>CountryMap- ADM 1 mean values</td><td>CountryMap- ADM 1 mean values</td></tr>
</table>

## Mean Anomaly

**CWD, SSP 126, Medium term**

<table>
  <tr><td>Mean</td><td>Standard Deviation</td></tr>
  <tr><td><img width=300 src="https://user-images.githubusercontent.com/44863827/159758502-5fa40db8-a2ab-498f-9339-e09f22808445.png"></td><td><img width=300 src="https://user-images.githubusercontent.com/44863827/159758595-72989fc4-ebc5-4ecd-b1c9-5391121a6fde.png"></td></tr>
  <tr><td>CountryMap- ADM 1 mean values</td><td>CountryMap- ADM 1 mean values</td></tr>
</table>

## Normalised Mean Anomaly

**CWD, SSP 126, Medium term**

<table>
  <tr><td>Mean</td><td>Standard Deviation</td></tr>
  <tr><td><img width=300 src="https://user-images.githubusercontent.com/44863827/159758502-5fa40db8-a2ab-498f-9339-e09f22808445.png"></td><td><img width=300 src="https://user-images.githubusercontent.com/44863827/159758595-72989fc4-ebc5-4ecd-b1c9-5391121a6fde.png"></td></tr>
  <tr><td>CountryMap- ADM 1 mean values</td><td>CountryMap- ADM 1 mean values</td></tr>
</table>

## Percentile 90th

**CWD, SSP 126, Medium term**

<table>
  <tr><td>Mean</td><td>Standard Deviation</td></tr>
  <tr><td><img width=300 src="https://user-images.githubusercontent.com/44863827/159758502-5fa40db8-a2ab-498f-9339-e09f22808445.png"></td><td><img width=300 src="https://user-images.githubusercontent.com/44863827/159758595-72989fc4-ebc5-4ecd-b1c9-5391121a6fde.png"></td></tr>
  <tr><td>CountryMap- ADM 1 mean values</td><td>CountryMap- ADM 1 mean values</td></tr>
</table>

## Percentile 99th

**CWD, SSP 126, Medium term**

<table>
  <tr><td>Mean</td><td>Standard Deviation</td></tr>
  <tr><td><img width=300 src="https://user-images.githubusercontent.com/44863827/159758502-5fa40db8-a2ab-498f-9339-e09f22808445.png"></td><td><img width=300 src="https://user-images.githubusercontent.com/44863827/159758595-72989fc4-ebc5-4ecd-b1c9-5391121a6fde.png"></td></tr>
  <tr><td>CountryMap- ADM 1 mean values</td><td>CountryMap- ADM 1 mean values</td></tr>
</table>
