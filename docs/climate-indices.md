# Climate indices

The climate component offers an overview of climate indices related to hydro-meteorological hazards based on the most updated climate modelling (**CMIP6**).
The [Climate Indices tools](run_ci) allow to compute climate indices for the desired sub-national boundary level.

The table summarises relationship between climate indices and hazard trends. 

|   Name   |                  Description                  |  Time-scale  |
|:--------:|:---------------------------------------------:|:------------:|
| R10mm    | Days with rainfall > 10 mm [days]             |    Annual    |
| Rx5day   | Maximum 5-day precipitation [mm]              |    Monthly   |
| R99p     | Extremely wet day precipitation [days]  	     |    Monthly   |
| CWD      | Consecutive Wet Days [days/month]             |    Annual    |
| CDD      | Consecutive Dry Days [days/month]             |    Annual    |
| slr      | Sea Level Rise [m]                            |    Annual    |
| SPEI     | Standard Precipitation-EvapoT Index [-]       |    Annual    |
| Heat     | WBGT or UTCI [°C] - bias adjusted             |     Daily    |
| tmean    | Mean surface temperature [°C]                 |    Monthly   |

## Data sources
The climate indices are primarily sourced from the [**WB Cimate Change Knowledge Portal**](https://climateknowledgeportal.worldbank.org).
Additional indices could also be obtained from external sources.

| **Name** | **Developer** | **Description** | **Data format** |
| --- |:---:|---|---|
| [Climate Knowledge portal](https://climateknowledgeportal.worldbank.org) | World Bank | Large selection of climate indices for both trends and extremes | Table, geodata, charts |
| [Climate Extreme Indices (CDS)](https://cds.climate.copernicus.eu/cdsapp#!/dataset/sis-extreme-indices-cmip6) | UNDRR | Full selection of variables, model members, periods | Geodata |
| [IPCC atlas](https://interactive-atlas.ipcc.ch/regional-information) | IPCC | Selection of climate variables for a range of periods and scenario | Table, geodata, maps, charts |
| [Global Drought Indices](https://data.ceda.ac.uk/badc/hydro-jules/data/Global_drought_indices) | CEDA | Global high-resolution drought datasets from 1981-2022 | Geodata |       

## Dimensions:
   - **SSP:** socio-climatic scenarios SSP1/RCP2.6, SSP2/RCP4.5, SSP3/RCP7.0, SSP5/RCP8
   - **Models ensemble range:** percentiles p10, p50, p90
   - **Period:** {Historical (1981-2015)}, [Near term (2020-2039), Medium term (2040-2059), Long term (2060-2079), End of century (2080-2099)]
   - **Time scale:** Annual (R10mm, CWD, slr, SPEI); Monthly (Rxday, R99p, tmean); Daily (Heat) 
   - **Value statistic:** {P10, P50, P90, SD}, [P10, P50, P90] 

