# OVERVIEW

The climate component offers an overview of climate indices related to hydro-meteorological hazards based on the most updated information (CMIP6).
The script climate component provides aggregated statistics at ADM level [1] or [0] for a selection of:
 1) climate-related hazards
 2) country
 3) time period

### Challenges:
- harvesting online data does not provide all the variables we want, especially for the critical step of normalisation
- the complete array of climate information is too large to be shared with the user and requires long processing. Thus the information needs to be aggregated into statistics
- we need to present a well-rounded perspective for both space and time dimension
- we can't have the cake and eat it too - or have the full bottle and the drunk wife

### The data input is:
- raster data aggregated across time (20 years windows) for spatial representation
- csv data aggregated across space (country scale) for time-serie representation

### The script does:

- Runs over one selected country and for a specific set of indices depending on selected hazard
- Consider three SSP (ex RCP) scenarios (2.6, 4.5, 8.5) by default and present them in the results
- Calculate output for selected period (near, medium and long term)
- The estimate is provided for median, 10th-percentile and 90th percentile
- ([confidence levels calculated as Ensemble_p25 and Ensemble_p75](https://climateinformation.org/confidence-and-robustness/how-to-interpret-agreement-ensemble-value-range/))
- Both the raster information andthe aggregated values at ADM1 or ADM0 level are plotted
- The results are exported as csv (table) and geopackage (vector)

### The output is:
- presented as maps (spatial distribution)
- plotted as charts (time distribution)
- exported in form of tables, statistics, charts (excel format) and maps (geopackage)

----------------------------

# PRE-PROCESSED CLIMATE INDICES

Climate data processing from CDS

**Version:** CMIP6 – GCM full collection

  - CMIP6 – [GCM projections](https://cds.climate.copernicus.eu/cdsapp#!/dataset/projections-cmip6)
    - pro: full selection of variables
    - con: raw variables, low resolution

  - CMIP6 derived [Climate Extreme Indices](https://cds.climate.copernicus.eu/cdsapp#!/dataset/sis-extreme-indices-cmip6)
    - pro: extreme indices already computed; refined resolution
    - con: does not include Wind, SLR, SPEI; rectangular grid

**Ensemble:** the largest number of models available for the required dimensions. 

Each index is stored as multiple multi-dimensional netcdf files. 

**Dimensions:** 
   - **SSP:** 2.6, 4.5, 8.5
   - **Ensemble member:** r1i1p1f1 
   - **Ensemble range (percentile):** 10, 50, 90
   - **Period:** {Historical (1981-2010)}, [Near term (2021-2040), Medium term (2041-2060), Long term (2081-2100)]
   - **Time scale:** Annual (R10mm, CWD, slr, SPEI); Monthly (Rxday, R99p, tmean); Daily (Heat) 
   - **Metric:** {Mean, Median, P10, P90, SD}, [Mean. Median, P10, P90] 


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

# SCRIPT STRUCTURE

- SETUP: environment and libraries
- USER INPUT: required
- DATA PROCESSING: datasets are processed according to settings
- PREVIEW RESULTS: plot tables and maps
- EXPORT RESULTS: results are exported as gpkg and csv according to templates

# SCRIPT STEP-BY-STEP

## SETUP

- Load required libraries
- Load data from geotiff and csv

## USER INPUT

- Hazard of interest (one selection or more):
  - [ ] Flood and Landslide
  - [ ] Drought and Water Scarcity
  - [ ] Heat stress
  - [ ] Tropical Cyclone
  - [ ] Coastal flood

- Country of interest (1): Name dropdown (link ISOa3 value) 

- Time period (one selection):
  - [ ] Near term (2021-2040)
  - [X] Medium term (2041-2060)
  - [ ] Long term (2081-2100)

------------------------------------------

## DATA PROCESSING - PROJECTIONS

- Compute the required spatial statistics based on the input selection (country/hazards) for all SSP and selected periods.
- Run zonal statistic using ADM1 as zone and nc data as value based on input (country, period, SSP) and settings aggregation criteria

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


## PREVIEW RESULTS

- Plot as maps including:
  - Projected Nornalised Mean Anonaly for selected period, all SSPs.
    - as raster data
    - as ADM1 mean value 

- Plot as chart including:
  - X is period last year (as from "period" input), Y is intensity (ramge depends on index and metric selection)
  - Historical Mean (black line) and SD (grey area around line)
  - Projected Normalised Mean Anomaly as 3 lines of different colors (green, yellow, orange) representing the median for each SSP
  - Projected Normalised Percentile 10th-90th as 3 color-shaded areas representing the p10-to-median and median-to-p90 for each SSP
  - Title and description of the aggregation criteria, e.g. "Median, p10 and p90 represent the mean of all models in the ensemble".
 
Similar to what usually done:

<img width="250" src="https://user-images.githubusercontent.com/44863827/159906283-e7c073dc-d88c-4de6-b9dd-331140bed8de.png">


## EXPORT RESULTS - PROJECTIONS

- Export output as gpkg and csv

<hr>

# EXAMPLE OUTPUT

## Flood hazard in Pakistan, Medium term 

### Maps - Spatial distribution

<table>
 <caption><b>Days with rainfall > 10 mm - Standardised anomaly, Medium term (2040-2060) compared to Historical period (1980-2010)</b></caption>
  <tr><td>SSP 2.6</td><td>SSP 4.5</td><td>SSP 8.5</td></tr>
  <tr><td><img width=300 src="https://user-images.githubusercontent.com/44863827/159758502-5fa40db8-a2ab-498f-9339-e09f22808445.png"></td>
   <td><img width=300 src="https://user-images.githubusercontent.com/44863827/159758595-72989fc4-ebc5-4ecd-b1c9-5391121a6fde.png"></td>
   <td><img width=300 src=""></td></tr>
</table>

<table>
 <caption><b>Maximum 5-day precipitation - Standardised anomaly, Medium term (2040-2060) compared to Historical period (1980-2010)</b></caption>
  <tr><td>SSP 2.6</td><td>SSP 4.5</td><td>SSP 8.5</td></tr>
  <tr><td><img width=300 src=""></td>
   <td><img width=300 src=""></td>
   <td><img width=300 src=""></td></tr>
</table>

<table>
 <caption><b>Very wet day precipitation - Standardised anomaly, Medium term (2040-2060) compared to Historical period (1980-2010)</b></caption>
  <tr><td>SSP 2.6</td><td>SSP 4.5</td><td>SSP 8.5</td></tr>
  <tr><td><img width=300 src=""></td>
   <td><img width=300 src=""></td>
   <td><img width=300 src=""></td></tr>
</table>


### Charts - Time distribution

<table>
 <caption><b>Standardised anomaly, Medium term (2040-2060) compared to Historical period (1980-2010)</b></caption>
  <tr><td>Days with rainfall > 10 mm</td><td>Maximum 5-day precipitation</td><td>Very wet day precipitation</td></tr>
  <tr><td><img width=300 src=""></td>
   <td><img width=300 src=""></td>
   <td><img width=300 src=""></td></tr>
</table>
