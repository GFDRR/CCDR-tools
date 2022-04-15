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
- Claulate median, 10th percentile (p10) and 90th percentile (p90) of standardised anomaly across models in the ensemble
- Compare standardised anomalies with pre-set thresholds to estimate change in the risk trend 
- Plot maps and timeseries
- The results are exported as csv (table) and geopackage (vector)

### The output is:
- presented as maps (spatial distribution)
- plotted as charts (time distribution)
- exported in form of tables, charts (excel format) and ADM 1 maps (geopackage)

### Resources and references:

- [E3CI](https://www.ifabfoundation.org/e3ci/)
- [IPCC atlas](https://interactive-atlas.ipcc.ch/regional-information)
- ([confidence levels calculated as Ensemble_p25 and Ensemble_p75](https://climateinformation.org/confidence-and-robustness/how-to-interpret-agreement-ensemble-value-range/))

----------------------------

# CLIMATE INDICES STATISTICS

The table summarises the relevant climate indices, with time scale and source. 

|   Name   |                  Description                  |     Source      | Time-scale  |
|:--------:|:---------------------------------------------:|:---------------:|:-----------:|
| R10mm    | Days with rainfall > 10 mm [days]             | CMIP6 Extremes  |   Annual    |
| Rx5day   | Maximum 5-day precipitation [mm]              | CMIP6 Extremes  |   Monthly   |
| R99p     | Extremely wet day precipitation [days]  	   | CMIP6 Extremes  |   Monthly   |
| CWD      | Consecutive Wet Days [days/month]             | CMIP6 Extremes  |   Annual    |
| CDD      | Consecutive Dry Days [days/month]             | CMIP6 Extremes  |   Annual    |
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
   - **Ensemble  range:** p10, p50, p90
   - **Period:** {Historical (1981-2015)}, [Near term (2020-2039), Medium term (2040-2059), Long term (2060-2079), End of century (2080-2099)]
   - **Time scale:** Annual (R10mm, CWD, slr, SPEI); Monthly (Rxday, R99p, tmean); Daily (Heat) 
   - **Value statistic:** {P10, P50, P90, SD}, [P10, P50, P90] 

These dimensions needs to be flatten according to meaningful statistics to provide aggregated outputs via the notebook.
Two types of output are produced:

A) Map output (spatial distribution)
   - raster data aggregated across time (20 years windows)
```
Ensemble_mean(Period_mean(anomaly/hist_SD))
Ensemble_p50(Period_mean(anomaly/hist_SD))
```
   - ADM1-mean values above or below threshold (no change, increase/decrease)
```
ADM1_mean(Ensemble_p50(Period_mean(anomaly/hist_SD))) ≥ Threshold = "Increase"
ADM1_mean(Ensemble_p50(Period_mean(anomaly/hist_SD))) < Threshold = "No change"
```
  
B) Chart output (time-series)
   - spatial data aggregated for country ADM0 boundaries plotted as chart
  ```
Ensemble_p10(ADM0_mean(anomaly/hist_SD))
Ensemble_p50(ADM0_mean(anomaly/hist_SD))
Ensemble_p90(ADM0_mean(anomaly/hist_SD))
  ```
## PROCESSING OF CLIMSTATS LAYERS FEEDING THE NOTEBOOK ANALYTICS

For each SSP scenario:
	for each period:
		for each model:
   
1. For each cell, calculate the anomaly and normalise it (anomaly/Hist_SD).
   - Result: anomaly value x n_models x time interval (annual, monthly or daily)
3. Take percentile 10, 50, 90 of these values to show the median change and the range of the variability within the model ensemble.
   - Result: in anomaly value x 3p x time interval
5. Calculate aggregated statistics:
   A) mean over future 20-years period for maps visualisation and threshold evaluation at ADM1.
   - Result: raster grid of anomaly x 3p
   - Result: ADM1 value (median) compared to thresholds 
   B) mean over ADM0 for timeseries visualisation up to end of selected period
   - Result: ADM0 anomaly x 3p x time interval. If the interval is monthly or daily, it could be further aggregated (moving average)

|          Hazard           |               Associated climate indices           |
|---------------------------|----------------------------------------------------|
| River floods / Wet Landslides | Consecutive Dry Days [days]                    |
|                           |     Days with rainfall > 10 mm [days]              |
|                           |     Maximum 5-day precipitation [mm]               |
|                           |     Very wet day precipitation [mm]      		 |
|     Coastal floods        |     Mean Sea Level Rise [m]                        |
|     Tropical cyclone      |     Number of days with strong winds [days]        |
|                           |     Daily maximum 10-m wind speed [m/s]            |
|     Agricultural drought  |     Standard Precipitation-ET Index (SPEI) [-]     |
|                           |     Consecutive Dry Days [days]                    |
|                           |     Consecutive Wet Days [days]                    |
|     Heat stress           |     Heat index [°C]                                |
|     Wildfire?             |     Standard Precipitation-ET Index (SPEI) [-]     |
|                           |     Heat index                                     |

## INPUT FILES FOR NOTEBOOK

The resulting statistics are exported as GeoTiff files and csv which are input for the notebook.

Geotiff files (global) are named: `timmean_[index_name]_[scenario]_[period]_ens[stat]_st.anomaly.tiff`

  - Example: `timmean_cwd_ssp126_2061-2080_enspctl,50_anomaly_std.tiff`

The number of .tiff files is n = (10 indices x (1 hist + 3 scenarios x 4 periods) x 3 stats) = 390 (~100 Kb each, ~40 Mb in total)

Csv files (for each country) are named: `[ISOa3]mean_[index_name]_st.anomaly_.csv`

  - Example: `PAKmean_rx5day_st.anomaly_.csv`

The number of files (for each country) is n = 10 indices x 1 sheet = 10 .csv files (or one .xlsx file),
where each sheet includes all scenarios and statistics covering all time range (size depends on time scale: annual or monthly)

---------------------


# RUNNING THE NOTEBOOK TO PRESENT CLIMATE DATA

## PRE-REQUISITES (OFFLINE)

- Anaconda and python installed > Possibly we move to jupyter desktop Autoinstaller
- Create environment from ccdr_analytics.yml

## NOTEBOOK SCRIPT STRUCTURE

- SETUP: environment and libraries
- USER INPUT: required
- DATA PROCESSING: datasets are processed according to settings
- PREVIEW RESULTS: plot maps and charts
- EXPORT RESULTS: results are exported as gpkg and csv according to templates

### SETUP

- Load required libraries

### USER INPUT

- Country of interest (1): Name dropdown (link ISOa3 value) 

- Hazard of interest (one selection):
  - [x] Flood and Landslide
  - [ ] Drought and Water Scarcity
  - [ ] Heat stress
  - [ ] Tropical Cyclone
  - [ ] Coastal flood

- Time period (one selection):
  - [ ] Near term (2020-2039)
  - [X] Medium term (2040-2059)
  - [ ] Long term (2060-2079)
  - [ ] End of century (2081-2100)


### PROCESSING

- Load .gpkg files (ADM1 units) according to country selection
- Load .tiff files (maps) according to hazard (one hazard can have multiple n indices) and time period selection (n_indices x (1 Historical + 3 SSP))
- Load .csv files (timeseries) according to hazard and country selection
- Load .csv file (indices thresholds)
- Run zonal stats using ADM1 units on map data using MEAN criteria over each selected index.
- Add field "Risk change" to ADM table
- Compare the ADM1 score with indices threshold;
  - if p50 > threshold, then: Risk_change = "Increase"
  - if p50 > threshold, then: Risk_change = "No change"

### PLOT RESULTS

For selected indices collection, SSP and period:

- Plot maps (20-years mean) as:
  - Grid data (1 row, 4 maps) showing (1) the historical p50 index value and (2-4) the p50 standard anomaly for 3 different SSP
  - ADM1 data (1 row, 4 maps) showing if the risk threshold is surpassed (two values: no change / increase)

- Plot timeseries (ADM0 mean) 
  - X is years up to period_end, Y is standardised anomaly (range depends on the index)
  - Black line: Historical p50 (10-years moving average)
  - Grey shade area: Historical p10-p90 range (10-years moving average)
  - 3 lines (green, yellow, orange) representing the Ensemble Median of St.Anomaly for each SSP (10-years moving average)
  - 3 color-shaded areas (light-green, -yellow, -orange) representing the Ensemble variability range p10-p90 for each SSP (10-years moving average)
  - Title and description of the aggregation criteria, e.g. "Median, p10 and p90 of ensemble for index (name)".
 
- Plot hazard/risk change (ADM1) for each index (map, chart or table)
  - Compare p50 of ensemble anomalies (50% confidence) with set threshold of change.
  - If the value is above threshold, the ADM1 is plotted as INCREASING

### EXPORT RESULTS - PROJECTIONS

- Export output as gpkg (ADM1 values) and csv (timeseries)

-------------------

# EXAMPLE OUTPUT

## Maps - Spatial distribution

### General template for one index / one period / multiple SSP / Historical value (index unit) and median anomaly (n of Standard Deviations compared to the historical period)

<img width=80% src="https://user-images.githubusercontent.com/44863827/162792641-87b8111b-41da-4ff3-9ed2-6d386659b2e1.png">

### Flood & Wet landslides, Medium Term (2040-2059)

<table>
 <caption><b>Consecutive Wet Days (CWD) - Standardised anomaly, Medium term (2040-2059) compared to Historical period (1980-2015)</b></caption>
  <tr><td><img width=80% src="https://user-images.githubusercontent.com/44863827/162793376-2960eb30-09e2-4384-896f-899192828a17.png"></td></tr>
</table>

<table>
 <caption><b>Days with precipitation over 10 mm - Standardised anomaly, Medium term (2040-2060) compared to Historical period (1980-2010)</b></caption>
  <tr><td><img width=80% src="https://user-images.githubusercontent.com/44863827/162793711-ad349487-dc46-4215-9e09-53b9682cf749.png"></td></tr>
</table>

<table>
 <caption><b>Very wet day precipitation - Standardised anomaly, Medium term (2040-2060) compared to Historical period (1980-2010)</b></caption>
  <tr><td><img width=80% src="https://user-images.githubusercontent.com/44863827/162793469-add447e9-656a-4572-92d0-750b9a7d8097.png"></td></tr>
</table>

<table>
 <caption><b>Maximum 5-day precipitation - Standardised anomaly, Medium term (2040-2060) compared to Historical period (1980-2010)</b></caption>
  <tr><td><img width=80% src="https://user-images.githubusercontent.com/44863827/162793424-a88c1a89-0ff9-4b23-8e6d-77b181f9ca8f.png"></td></tr>
</table>

## Charts - Time distribution

<table>
 <caption><b>Standardised anomaly, Medium term (2040-2060) compared to Historical period (1980-2010)</b></caption>
  <tr><td>Days with rainfall > 10 mm</td><td>Maximum 5-day precipitation</td><td>Very wet day precipitation</td></tr>
  <tr><td><img width=300 src=""></td>
   <td><img width=300 src="https://github.com/klee016/SAR-CCDR-visualizations/raw/main/Pakistan/R%20Markdown/01.chapter1_files/figure-gfm/unnamed-chunk-44-1.png"></td>
   <td><img width=300 src=""></td></tr>
</table>


## Table (for dynamic visualisation)

| time | HIST_SD | Hist_p10 | Hist_50 | Hist_p90 | ssp(i)_pc10 | ssp(i)_pc50 | ssp(i)_pc90 | Std_Anom_Hist_p10 | Std_Anom_Hist_50 | Std_Anom_Hist_p90 | Std_Anom_ssp(i)_pc10 | Std_Anom_ssp(i)_pc50 | Std_Anom_ssp(i)_pc90 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1980 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 1981 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 1982 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 1983 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 1984 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| ... |  |  |  |  |  |  |  |  |  |  |  |  |  |
