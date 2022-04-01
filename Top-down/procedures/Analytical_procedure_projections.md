# OVERVIEW

The climate component offers an overview of climate indices related to hydro-meteorological hazards based on the most updated information (CMIP6).
The script climate component provides aggregated statistics at ADM level [1] or [0] for a selection of:
 1) climate-related hazards
 2) country
 3) time period

Compared to the information offered by the [CCKP country page](https://climateknowledgeportal.worldbank.org/country/pakistan/climate-data-projections), this procedure adds:
- Linking indices to hazards, thresholds to estimate change for ADM1 (increse / no change / decrease)
- Standardisation of anomaly over historical variability as common metric of comparison

### Challenges:
- harvesting online data does not provide all the variables we want, especially for the critical step of spatial standardisation/normalisation
- the complete array of climate information is too large to be shared with the user and requires long processing. Thus the information needs to be aggregated into statistics
- we need to present a well-rounded perspective for both space and time dimension

### The input data is:
- raster data aggregated across time (20 years windows) for spatial representation
- csv data aggregated across space (country boundaries) for time-serie representation
  - includes ensemble p10 and p90 (variability across models)

### The script does:

- Runs over one selected country and for a specific set of indices depending on selected hazard
- Consider three SSP (ex RCP) scenarios (2.6, 4.5, 8.5) by default and present them in the results
- Consider four future 20-years period (near term, medium term, long term, end of century)
- Claulate median, 10th percentile (p10) and 90th percentile (p90) of standardised anomaly
- Compare standardised anomalies with pre-set thresholds to estimate change in the risk trend 
- Plot maps and timeseries
- The results are exported as csv (table) and geopackage (vector)

### The output is:
- presented as maps (spatial distribution)
- plotted as charts (time distribution)
- exported in form of tables, statistics, charts (excel format) and maps (geopackage)

### Resources and references:

- [E3CI](https://www.ifabfoundation.org/e3ci/)
- [IPCC atlas](https://interactive-atlas.ipcc.ch/regional-information)
- ([confidence levels calculated as Ensemble_p25 and Ensemble_p75](https://climateinformation.org/confidence-and-robustness/how-to-interpret-agreement-ensemble-value-range/))

----------------------------

# PRE-PROCESSED CLIMATE INDICES

The table summarises the relevant climate indices, with time scale and source. 

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


**Sources:** CMIP6 – GCM full collection

  - CMIP6 – [GCM projections (CDS)](https://cds.climate.copernicus.eu/cdsapp#!/dataset/projections-cmip6)
    - pro: full selection of variables
    - con: raw variables, low resolution

  - CMIP6 derived [Climate Extreme Indices (CDS)](https://cds.climate.copernicus.eu/cdsapp#!/dataset/sis-extreme-indices-cmip6)
    - pro: extreme indices already computed; refined resolution
    - con: does not include Wind, SLR, SPEI; rectangular grid

Each index is downloaded  as multiple multi-dimensional netcdf files. 

**Dimensions:** 
   - **SSP:** 1 (2.6), 2 (4.5), 5 (8.5)
   - **Ensemble member:** r1i1p1f1 (largest number of models available)
   - **Ensemble  range:** mean, p10, p90
   - **Period:** {Historical (1981-2015)}, [Near term (2020-2039), Medium term (2040-2059), Long term (2060-2079), End of century (2080-2099)]
   - **Time scale:** Annual (R10mm, CWD, slr, SPEI); Monthly (Rxday, R99p, tmean); Daily (Heat) 
   - **Value statistic:** {Median, P10, P90, SD}, [Median, P10, P90] 

These dimensions needs to be flatten according to meaningful statistics to provide aggregated outputs.
The script produces two types of output:

A) Map output (spatial distribution)
   - raster data aggregated across time (20 years windows)
   - ADM1-mean values above or below threshold (no change, increase/decrease)
  ```
Period_mean(Ensemble_p10(anomaly/hist_SD))
Period_mean(Ensemble_p50(anomaly/hist_SD))
Period_mean(Ensemble_p90(anomaly/hist_SD))

  ```
  
B) Chart output (time-series)
   - spatial data aggregated for country ADM0 boundaries plotted as chart
  ```
ADM0_mean(Ensemble_p10(anomaly/hist_SD))
ADM0_mean(Ensemble_p50(anomaly/hist_SD))
ADM0_mean(Ensemble_p90(anomaly/hist_SD))
  ```

# PRE-REQUISITES (OFFLINE)

- Anaconda and python installed > Possibly we move to jupyter desktop Autoinstaller
- Create environment from ccdr_analytics.yml

# SCRIPT STRUCTURE

- SETUP: environment and libraries
- USER INPUT: required
- DATA PROCESSING: datasets are processed according to settings
- PREVIEW RESULTS: plot maps and charts
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
| River floods / Wet Landslides |     Days with rainfall > 10 mm [days]              |
|                           |     Maximum 5-day precipitation [mm]               |
|                           |     Very wet day precipitation [days/month]        |
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
  - X is period last year (as from "period" input), Y is intensity (ramge depends on index and statistic selection)
  - Historical Mean (black line) and SD (grey area around line)
  - Projected Normalised Mean Anomaly as 3 lines of different colors (green, yellow, orange) representing the median for each SSP
  - Projected Normalised Percentile 10th-90th as 3 color-shaded areas representing the p10-to-median and median-to-p90 for each SSP
  - Model confidence level as shaded area ranging p25-p75
  - Title and description of the aggregation criteria, e.g. "Median, p10 and p90 represent the mean of all models in the ensemble".
 
Similar to what usually done:

<img width="250" src="https://user-images.githubusercontent.com/44863827/159906283-e7c073dc-d88c-4de6-b9dd-331140bed8de.png">


## EXPORT RESULTS - PROJECTIONS

- Export output as gpkg and csv

<hr>

# EXAMPLE OUTPUT

### Maps - Spatial distribution

<table>
 <caption><b>Consecutive Wet Days (CWD) - Standardised anomaly, Medium term (2040-2060) compared to Historical period (1980-2010)</b></caption>
  <tr><td><img width=100% src="https://user-images.githubusercontent.com/44863827/160589506-0cc713b0-5a4e-4efb-8159-970b94087ca5.png"></td></tr>
</table>

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
