# Expected Annual Exposure (EAE) 

## OBJECTIVE

The script performs combination of hazard and exposure geodata from global datasets according to user input and settings, and returns a risk score in the form of Expected Annual Exposure (EAE) for the baseline (reference period). 

The "classes" approach simply split the hazard intensity layer into classes and, for ach one, calculates the toal exposure for the selected category. 
For example, flood hazard over agriculture is measured in terms of hectars of land falling within different intervals of water depth.
Note that Minimum threshold is deactivated/ignored for this approach.

The spatial information about hazard and exposure is first collected at the grid level, the output is then aggregated at ADM2 boundary level to combine Vulnerability scores and calculate risk estimate. This represents the disaster risk historical baseline.

The output is exported in form of tables, statistics, charts (excel format) and maps (geopackage).

## SCRIPT OVERVIEW

- For now, each script is hazard specific, because each hazard has its own metrics and thresholds; we are looking to build a better interface.
- Script runs on one country at time to keep the calculation time manageable.
- The analysis is carried at the resolution of the exposure layer. For now, it is set around 100m.
- User input is required to define country, exposure layer, and settings.
- Settings affect how the processing runs (number of classes and intervals).
- The core of the analysis is raster calculation: how much population falls in each class of hazard.
- The information is aggregated at desired ADM level using zonal statistics
- The expected annual impact (EAE) is computed by summing up the total impact over a certain class threshold. For example, when considering agricultural flood impacts, it may account only for water depth > 0.5 m. Exposure score is multiplied by the exceedence frequency (1/RPi - 1/RPj) of the scenario. The exceedance frequency curve (EFC) is built and plotted.
- Table results are exported in excel format, map rsults are exported in gpkg format.

## SCRIPT STRUCTURE

- SETUP: environment and libraries
- USER INPUT: specify country and categories of interest
- SETTINGS: default parameters can be changed by user
- DATA MANAGEMENT: global datasets are loaded according to user input
- DATA PROCESSING: datasets are processed according to settings
- PREVIEW RESULTS: plot tables and maps
- EXPORT RESULTS: results are exported as excel according to template

## PRE-REQUISITES

- Latest Anaconda and Python properly installed, environment set as from [instructions](../notebooks#readme).

## SCRIPT STEP-BY-STEP

### USER INPUT & SETTINGS (DEFAULTS can be changed)
- Country (1): Name or ISO code 
- Exposure category (1): a) population; b) built-up; c) agricultural land
- Number of classes: 5 (2 to 10)
- Min class threshold: starting value of each class, up to the next. Last class goes to infinite.

<img width=200 src="https://user-images.githubusercontent.com/44863827/156603360-dabc7da2-52c8-4ed2-be07-bd2a4927af16.png">

### DATA MANAGEMENT

- Load country boundaries for multiple administrative levels sourced from [HDX](https://data.humdata.org/dataset) or [Geoboundaries](https://www.geoboundaries.org). Note that oftern there are several versions for the same country, so be sure to use the most updated from official agencies (eg. United Nations).

- Verify that shapes, names and codes are consistent across different levels.

- Load exposure data
  - Population: WorldPop 2020 Population counts / Constrained individual countries, UN adjusted (100 m resolution)
	-  [Download page](https://hub.worldpop.org/geodata/listing?id=79)
	-  API according to ISO3 code: https://www.worldpop.org/rest/data/pop/wpgp?iso3=NPL
    	returns a Json that includes the url of data: https://data.worldpop.org/GIS/Population/Global_2000_2020/2020/NPL/npl_ppp_2020.tif
  - Built-up: the latest [World Settlement footprint](https://download.geoservice.dlr.de/WSF2019/#details) can be download as tiles for the area of interest and merged into one compressed tif. 10 m binary grid can be resampled into 100 m using "mean": returns a 0-1 ratio describing the share of builtup for 100m cell.
  - Land cover / Agricultural land: many are available from [planeterycomputer catalog](https://planetarycomputer.microsoft.com/catalog#Land%20use/Land%20cover). ESA 2020 at 10m resolution is suggested. Specific land cover types can be filtered using pixel value.

- Load hazard data.
	- Most hazard data consist of multiple layers (Return Periods, RP) each representing one probabilistic intensity maximum, or in other words the intensity of the hazard in relation to its frequency of occurrence.
	- Some hazards, however, comes as individual layers representing a mean hazard value. In this case, ignore the looping over RP.

### DATA PROCESSING

- LOOP over each hazard RPi layers:
  - Classify hazard layer RPi according to settings: number and size of classes: `RPi` -> `RPi_Cj` (multiband raster)
  - Each class `Cj` of RPi is used to mask the Exposure layer -> `RPi_Cj_Exp` (multiband raster)
  - Perform zonal statistic (SUM) for each ADMi unit over eac `RPi_Cj_Exp` -> `table [ADMi_NAME;RPi_C1_Exp;RPi_C2_Exp;...RPi_Cj_Exp]`<br>
    Example using 3 RP scenarios: (10-100-1000) and 3 classes (C1-3): `table [ADM2_NAME;RP10_C1_Exp;RP10_C2_Exp;RP10_C3_Exp;RP100_C1_Exp;RP100_C2_Exp;RP100_C3_Exp;RP1000_C1_Exp;RP1000_C2_Exp;RP1000_C3_Exp;]

- Calculate EAE
  - Calculate the exceedance frequency for each RPi -> `RPi_ef = (1/RPi - 1/RPi+1)` where `RPi+1` means the next RP in the serie.
    Example using 3 RP scenarios: RP 10, 100, and 1000 years. Then: `RP10_ef = (1/10 - 1/100) = 0.09`
  - Multiply exposure for each scenario i and class j `(RPi_Cj_Exp)` with its exceedence frequency `(RPi_ef)` -> `RPi_Cj_Exp_EAE`
  - Sum `RPi_Cj_Exp_EAE`across multiple RPi for the same class Cj -> `table [ADMi;Cj_Exp_EAE]`<br>
    Example using 3 classes (C1-3): `table [ADMi;C1_Exp_EAE;C2_Exp_EAE;C3_Exp_EAE]`

	| RP | Exceedance freq | C3 | C4 | C5 | C6 | C3-6 | C3_EAE | C4_EAE | C5_EAE | C6_EAE | C3-6_EAE |
	|:---:|---|:---:|:---:|:---:|:---:|---|:---:|:---:|:---:|:---:|---|
	| 10 | 0.09 | 4,036 | 1,535 | 2,111 | 1,967 | 9,658 | 363 | 138 | 190 | 177 | 868 |
	| 100 | 0.009 | 8,212 | 5,766 | 5,007 | 13,282 | 32,367 | 739 | 519 | 451 | 1,195 | 2,904 |
	| 1000 | 0.0009 | 8,399 | 5,134 | 4,371 | 25,989 | 44,893 | 756 | 462 | 393 | 2,339 | 3,950 |
	| Total | | | | | | | 1,858 | 1,119 | 1,034 | 3,711 | 7,723 |
  
  - Plot Exceedance Frequency Curve. Example:<br>
    ![immagine](https://user-images.githubusercontent.com/44863827/198069028-8bd0e317-0b2e-4a22-b912-e260d3b3bd65.png)
  - Perform zonal statistic of Tot_Exp using ADMi -> `[ADMi;ADMi_Exp;Exp_EAE]` in order to calculate `Exp_EAE% = Exp_EAE/ADMi_Exp` -> `[ADMi;ADMi_Exp;Exp_EAE;Exp_EAE%]`

## PREVIEW RESULTS
- Plot map of ADMi_EAE and related tables/Charts

## EXPORT RESULTS
- Export geodata output as gpkg and tables, generate charts

--------------------------------------

## EQUIVALENT PROCESSING IN QGIS

The following display equivalent spatial analytics steps performed by the script by using QGIS (well known, free geospatial tool).

### DATA MANAGEMENT

- Load map data: ADM units (3 layers), hazard (one or as many layers as RP scenarios) and exposure (population map, land cover, etc).
  In this example, we use FATHOM river flood data (light blue) and WorldPop2020-constrained-US_adjusted population data (green to purple).

  <img width=50% src="https://user-images.githubusercontent.com/44863827/151433893-76299364-f416-487f-a3e1-acf082d8b137.png">

- (optional) assign symbology for each one to print out readable maps. Consider min and max hazard thresholds and classes when building symbology.

  <img width=50% src="https://user-images.githubusercontent.com/44863827/151356576-7f56d2a6-4314-4bcb-9727-377bd032ac54.png">

### ANALYTICAL APPROACH

In this scenario, the physical hazard intensity is ranked in qualitative classes of impact magnitude. This is the case when no impact function is available for the category at risk, but a classification of impact by hazard thresholds is possible. Starting from the thresholded layer, we split the hazard intensity (water depth, as in previouse example) into 6 classes, each representing an interval of water depth range in m - except the last one, the includes all values > MAX damage ratio. Then, we extract the total population located within each hazard class for each ADM3 unit into an excel table for further analytics to be applied.

Water depth classes:
|Class name| min | Max | 
|--|-----|---|
|C1| 0.01 | 0.15 |
|C2| 0.15 | 0.5 |
|C3| 0.5 | 1 |
|C4| 1 | 1.5 |
|C5| 1.5 | 2 |
|C6| 2 | inf |

- Raster calculator: split the layer (one layer or multiple RP) into multiple impact classes. Repeat the task, changing the interval values for each class. 

  <img width=40% src="https://user-images.githubusercontent.com/44863827/153635133-40167c5e-6e99-45a5-add7-8f116fe78512.png">

  The outputs are 6 raster files, one for each hazard class, as a binary mask. These can combined into one multi-band file.
  
- Merge tool: select the 6 layers and keep default options; select "High" compression.

  <img width=40% src="https://user-images.githubusercontent.com/44863827/151591267-4b7706e5-1d12-4bca-a4bf-2163f7f7572e.png">

  Resulting multi-band file (each band plotted separately):
  
  <img width=50% src="https://user-images.githubusercontent.com/44863827/151594139-4583cdc4-1bc0-4961-a860-dbc4cb826366.png">

- Raster calculator: multiply each band from the multi-band file with the population map.

  <img width=40% src="https://user-images.githubusercontent.com/44863827/151592373-e01086a2-e9fb-4f50-9f37-fd9dfb029f51.png">

  The outputs are 6 raster files, one for each hazard class, as number of exposed population. These can combined into one multi-band file (class_population), as shown before.
  Resulting multi-band file (each band plotted separately) in orange-red colors:

  <img width=50% src="https://user-images.githubusercontent.com/44863827/151594269-268fbf44-882d-46a1-a610-65d5abca12af.png">

- Zonal statistic: run as "batch". Select the 6 bands of the multi-band class_population layer, and select only the "sum" criteria to aggregate impacted population at ADM3 level.

  <img width=50% src="https://user-images.githubusercontent.com/44863827/151595290-3951d11e-85dc-4d7b-af70-9c8741c651d3.png">

  Six columns [c1_sum to c6_sum] are added to ADM3 layer. It can be plotted to represent the number of people wihith each hazard class; or it can be exported as table for further steps of the analytics (e..g apply desired functions or parameters to each class). You can do that by either 1) exporting the ADM3 layer as csv; or 2) selecting the whole attribute table and selecting the "copy" button on the top (ctrl+C does not work!). Then paste into excel.
  
  <img width=50% src="https://user-images.githubusercontent.com/44863827/151596863-ec6d47cd-b2c7-4511-8ef3-d5275f01ea46.png">

  In order to express the value as % of total, the steps are the same as explained in the Option 1 example: extract total population using zonal statistic, and export it as table.
