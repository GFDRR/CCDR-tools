# Climate indices

The climate component offers an overview of climate indices related to hydro-meteorological hazards based on the most updated information (CMIP6).
The script climate component provides aggregated statistics at ADM level [1] or [0] for a selection of:
 1) climate-related hazards
 2) country
 3) time period

Compared to the information offered by the [CCKP country page](https://climateknowledgeportal.worldbank.org/country/pakistan/climate-data-projections), this procedure adds:
- Linking relevant climate indices to natural hazard occurrance in order to estimate change at ADM1 level
- Standardisation of anomaly over historical variability as common metric of comparison

## Challenges:
- harvesting online data does not provide all the variables we want, especially for the critical step of spatial standardisation/normalisation
- the complete array of climate information is too large to be shared with the user and requires long processing. Thus the information needs to be aggregated into statistics
- we need to present a well-rounded perspective for both space and time dimension

## The input data is:
- raster data aggregated across time (20 years windows) for spatial representation
- csv data aggregated across space (country boundaries) for time-serie representation
  - includes ensemble p10 and p90 (variability across models)

## The script does:

- Runs over one selected country and for a specific set of indices depending on selected hazard
- Consider four SSP (ex RCP) scenarios (SSP1/RCP2.6; SSP2/RCP4.5; SSP3/RCP7.0; SSP5/RCP8.5)
- Consider four 20-years periods (near term, medium term, long term, end of century)
- Calculate median, 10th percentile (p10) and 90th percentile (p90) of standardised anomaly across models in the ensemble
- Plot maps and timeseries
- Exported results as csv (table) and geopackage (vector)

## The output is:
- presented as maps (spatial distribution)
- plotted as charts (time distribution)
- exported in form of tables, charts (excel format) and ADM 1 maps (geopackage)

## Resources and references:

- [E3CI](https://www.ifabfoundation.org/e3ci/)
- [IPCC atlas](https://interactive-atlas.ipcc.ch/regional-information)
- [Confidence levels calculated as Ensemble_p25 and Ensemble_p75](https://climateinformation.org/confidence-and-robustness/how-to-interpret-agreement-ensemble-value-range/)

----------------------------

# CLIMATE INDICES STATISTICS

The table summarises the relevant climate indices, with time scale and source. 

|   Name   |                  Description                  |  Time-scale  |
|:--------:|:---------------------------------------------:|:------------:|
| R10mm    | Days with rainfall > 10 mm [days]             |    Annual    |
| Rx5day   | Maximum 5-day precipitation [mm]              |    Monthly   |
| R99p     | Extremely wet day precipitation [days]  	   |    Monthly   |
| CWD      | Consecutive Wet Days [days/month]             |    Annual    |
| CDD      | Consecutive Dry Days [days/month]             |    Annual    |
| slr      | Sea Level Rise [m]                            |    Annual    |
| sfcWind  | Daily maximum 10-m wind speed                 |    Annual    |
|          | Number of days with strong winds [days]       |    Monthly   |
| SPEI     | Standard Precipitation-ET Index [-]           |    Annual    |
| Heat     | WBGT or UTCI [°C] - bias adjusted             |     Daily    |
| tmean    | Mean surface temperature [°C]                 |    Monthly   |


### Sources of CMIP6 data

- **WB Climate Knowledge portal**
  *pro:* large selection of indices for trens and extremes; geodata export; chart generation

- **[GCM projections (CDS)](https://cds.climate.copernicus.eu/cdsapp#!/dataset/projections-cmip6)**
  - *pro:* full selection of variables
  - *con:* raw variables, low resolution

- CMIP6 derived [Climate Extreme Indices (CDS)](https://cds.climate.copernicus.eu/cdsapp#!/dataset/sis-extreme-indices-cmip6)
  - *pro:* extreme indices already computed; refined resolution
  - *con:* does not include Wind, SLR, SPEI; rectangular grid

Each index is downloaded as multiple multi-dimensional netcdf files. 

### Dimensions:
   - **SSP:** SSP1/RCP2.6; SSP2/RCP4.5; SSP3/RCP7.0; SSP5/RCP8
   - **Ensemble member:** r1i1p1f1 (largest number of models available)
   - **Ensemble  range:** p10, p50, p90
   - **Period:** {Historical (1981-2015)}, [Near term (2020-2039), Medium term (2040-2059), Long term (2060-2079), End of century (2080-2099)]
   - **Time scale:** Annual (R10mm, CWD, slr, SPEI); Monthly (Rxday, R99p, tmean); Daily (Heat) 
   - **Value statistic:** {P10, P50, P90, SD}, [P10, P50, P90] 

These dimensions needs to be flatten according to meaningful statistics to provide aggregated outputs via the notebook.
Two types of output are produced:

### Data processing and presentation

**A) Map output** (spatial distribution)
   - Raster data aggregated across time (20 years windows)
```
Ensemble_mean(Period_mean(anomaly/hist_SD))
Ensemble_p50(Period_mean(anomaly/hist_SD))
```
   - ADM1-mean values from raster data
```
ADM1_mean(Ensemble_p50(Period_mean(anomaly/hist_SD)))
```
  
**B) Chart output** (time-series)
   - Spatial data aggregated for country ADM0 boundaries plotted as chart
  ```
Ensemble_p10(ADM0_mean(anomaly/hist_SD))
Ensemble_p50(ADM0_mean(anomaly/hist_SD))
Ensemble_p90(ADM0_mean(anomaly/hist_SD))
  ```