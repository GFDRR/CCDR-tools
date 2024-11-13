(climate-change-and-disaster-risk)=
# Climate change and disaster risk
Climate change can increase disaster risk in a variety of ways:
- by altering the frequency, intensity and geographic distribution of weather-related hazards, which may lead to new patterns of risk.
- by affecting vulnerability to hazards, and changing exposure patterns.

In other words, disaster risk can be magnified by climate change: it can increase the hazard while at the same time decreasing the resilience of households and communities. Below are some of the main changes expected by the [IPCC Sixth Assessment Report](https://www.ipcc.ch/report/sixth-assessment-report-cycle/).

- **Storms and flooding:** the water cycle will continue to intensify as the planet warms. That includes extreme monsoon rainfall, but also increasing drought, greater melting of mountain glaciers, decreasing snow cover and earlier snowmelt. Annual average precipitation is projected to increase in many areas as the planet warms, particularly in the higher latitudes.

- **Sea level rise:** the population of coastal areas has grown faster than the overall increase in global population; coastal flooding events could threaten assets worth up to 20% of the global GDP by 2100. Low-lying island states could be completely wiped out by sea level rise.

- **Heat stress:** the most direct impact of global warming will be an increase of temperatures, which will aggravate heat stress consequences on human health and agricultural production, in particular in tropical countries with low capacity for adaptation.

- **Droughts:** there will likely be a large reduction in natural land water storage in two-thirds of the world, especially in the Southern Hemisphere. The number of people suffering extreme droughts across the world could double in less than 80 years, which has major implications for the livelihoods of the rural poor, and can also lead to increased migration streams.

- **Tropical cyclones:** even though the attribution of these events to climate change is difficult, a robust increase of the most devastating storms with climate change is expected. Under 2.5°C of global warming, the most devastating storms are projected to occur up to twice as often as today.

Hydro-meteorological hazards are affected by climate forcing, and, as such, climate change should be accounted when estimating future risk conditions. A forward-looking analysis makes use of climate projections to explore how environmental risks could develop spatially over time.

## Climate indices
Climate indices are standardized measurements used to track and summarize complex climate patterns over time. These indices distill vast amounts of climate data, such as temperature, precipitation, and atmospheric pressure, into simpler, more understandable metrics. By providing insights into trends and variations in these phenomena, climate indices assist in predicting weather patterns, understanding climate variability, and informing climate-related decisions across various sectors.

In the context of disaster risk, climate indices play a critical role in understanding and anticipating the impact of climate-related hazards. These indices help assess the likelihood of extreme weather events such as droughts, floods, hurricanes, and heatwaves by tracking patterns in atmospheric and oceanic conditions that influence climate variability. Projected changes of climate indices against  baseline (anomalies) can be used to infer changes in natural hazard frequency and intensity. 

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
Heat stress | Heat index (WBGT or UTCI) for *moderate* or *extreme* stress | Days per year
```

Given that specific unit of measurement varies across climate indices, in order to give a comparable metric of change the projected anomalies against the baseline are expressed in terms of Standard Deviation (SD) of the anomaly compared to historical variability [E3CI, 2020](https://www.ifabfoundation.org/e3ci/).
Data from climate models released under the [IPCC Sixth Assessment Report (AR) framework](https://www.ipcc.ch/assessment-report/ar6/) are used to establish estimates of baseline and future projected climate anomalies. ARs are supported by coordinated climate modeling efforts referred to as Coupled Model Intercomparison Projects (**CMIP**).

The analysis relies on **CMIP6** data for modeling into the future, and takes into account four climate change scenarios, referred to as Shared Socioeconomic Pathways (SSPs) in CMIP6. These pathways cover the range of possible future scenarios of anthropogenic drivers of climate change by accounting for various future greenhouse gas emission trajectories, as well as a specific focus on carbon dioxide (CO2) concentration trajectories (IPCC 2021b).

Guidance for aligned scenario selection is provided by the shared [**CCDR Global Climate Scenarios note**](https://github.com/GFDRR/CCDR-tools/blob/main/docs/CCDR_notes/CCDR%20Global%20Climate%20Scenarios.pdf).

```{figure} images/climate_scenarios.png
---
width: 100%
align: center
---
Recommended CCDR Global Scenarios and characteristics for adaptation and development planning.
```
- **SSP1-1.9 / RCP2.6:** emissions peak between 2040 and 2060, declining by 2100. This results in warming of 3-3.5 °C by 2100.
- **SSP2-4.5 / RCP4.5:** emissions continue to increase through the end of the century, with resulting warming of 3.8-4.2 °C by 2100.
- **SSP3-7.0 / RCP8.5:** models describe a large emission variability for this scenario. Warming is estimated at 3.9-4.6 °C by 2100.

Each climate scenarios predicts different spatial patterns, resulting into a range of possible futures in terms of intensities, and frequencies of natural hazards. Key climate variables connected to the changing patterns of precipitation and temperature are collected from the [Climate Change Knowledge Portal](https://climateknowledgeportal.worldbank.org/) and the [Copernicus Data Store](https://cds.climate.copernicus.eu/cdsapp#!/dataset/sis-extreme-indices-cmip6).

```{seealso}
- The [**Climate Knowledge Portal**](https://climateknowledgeportal.worldbank.org) by the World Bank provides a large selection of climate indices for both trends and extremes as table, geodata and charts.
- The [**Climate analytics repository**](https://bennyistanto.github.io/gost-climate) by the Global Operational Support Team (**GOST**) describes a list of data provider, derived products, step-by-step to do the analysis to produce climate analytics.
- The [**CLIMADA project**](https://github.com/CLIMADA-project/climada_python) by ETH Zurich provides global coverage of major climate-related extreme-weather hazards at high resolution via data API.
- The [**European Extreme Events Climate Index**](https://www.ifabfoundation.org/e3ci/) based on the [Actuaries Climate Index (ACI)](https://actuariesclimateindex.org) offers an ensemble of indices to describe different types of weather-induced hazards and their severity.
```

