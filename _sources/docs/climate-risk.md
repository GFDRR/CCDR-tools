# Climate outlook

Hydro-meteorological hazards are affected by climate forcing, and, as such, climate change should be accounted when estimating future risk conditions. A forward-looking analysis makes use of climate projections to explore how environmental risks could develop spatially over time.

```{figure} images/hzd_spectrum.png
---
width: 100%
align: center
---
```

The estimate of upcoming climate change impacts are based on comparisons of baseline conditions (which can be either observed or simulated) against future scenarios of climate variability. The long-term averages of climate variables serve as the baseline conditions. Changes in projected values against this baseline are then interpreted future climate anomalies and used to project forward-looking disaster risks.

```{table} Climate variables underlying hazard projections
:name: climate_indices
**Hazard** | **Associated climate indices** | **Unit of measurement**
---:|---|---
Floods and Landslides | Rainfall > 10 mm | Days per year
Floods and Landslides | Consecutive wet days | Days per year
Floods and Landslides | Maximum 5-day precipitation | mm
Floods and Landslides | Extremely wet days | mm
Coastal floods | Sea Level Rise	| m
Drought	| Annual SPEI | [-]
Drought	| Consecutive dry days | Days per year
Heat stress | Heat index (WBGT or UTCI) for *moderate stress* | Days per year
Heat stress | Heat index (WBGT or UTCI) for *extreme stress* | Days per year
```

Given that specific unit of measurement varies across climate indices, in order to give a comparable metric of change the projected anomalies against the baseline are expressed in terms of Standard Deviation (SD) of the anomaly compared to historical variability [E3CI, 2020](https://www.ifabfoundation.org/e3ci/).
Data from climate models released under the IPCC Sixth Assessment Report (AR) framework (IPCC 2021a) are used to establish estimates of baseline and future projected climate anomalies. ARs are supported by coordinated climate modeling efforts referred to as Coupled Model Intercomparison Projects (**CMIP**).

The analysis relies on **CMIP6** data for modeling into the future, and takes into account four climate change scenarios, referred to as Shared Socioeconomic Pathways (SSPs) in CMIP6. These pathways cover the range of possible future scenarios of anthropogenic drivers of climate change by accounting for various future greenhouse gas emission trajectories, as well as a specific focus on carbon dioxide (CO2) concentration trajectories (IPCC 2021b). The following scenarios are included in this analysis:

- **SSP1/RCP2.6:** emissions peak between 2040 and 2060, declining by 2100. This results in warming of 3-3.5 °C by 2100.
- **SSP2/RCP4.5:** emissions continue to increase through the end of the century, with resulting warming of 3.8-4.2 °C by 2100.
- **SSP3/RCP7.0:** models describe a large emission variability for this scenario. Warming is estimated at 3.9-4.6 °C by 2100.
- **SSP5/RCP8.5:** high emissions scenario resulting in warming of 4.7-5.1 °C by 2100.

Each climate scenarios predicts different spatial patterns, resulting into a range of possible futures in terms of intensities, and frequencies of natural hazards. Key climate variables connected to the changing patterns of precipitation and temperature are collected from the [Climate Change Knowledge Portal](https://climateknowledgeportal.worldbank.org/) and the [Copernicus Data Store](https://cds.climate.copernicus.eu/cdsapp#!/dataset/sis-extreme-indices-cmip6).

```{seealso}
- The [**Climate Knowledge Portal**](https://climateknowledgeportal.worldbank.org) by the World Bank provides a large selection of climate indices for both trends and extremes as table, geodata and charts.
- The [**Climate analytics repository**](https://bennyistanto.github.io/gost-climate) by the Global Operational Support Team (**GOST**) describes a list of data provider, derived products, step-by-step to do the analysis to produce climate analytics.
- The [**CLIMADA project**](https://github.com/CLIMADA-project/climada_python) by ETH Zurich provides global coverage of major climate-related extreme-weather hazards at high resolution via data API.
- The [**European Extreme Events Climate Index**](https://www.ifabfoundation.org/e3ci/) based on the [Actuaries Climate Index (ACI)](https://actuariesclimateindex.org) offers an ensemble of indices to describe different types of weather-induced hazards and their severity.
```

