# ANALYTICAL APPROACH = Expected Annual Impact (EAI) 

This analytical approach applies to multiple probabilistic hazard scenarios and aims to produce a mean estimate of Expected Annual Impact (EAI).

<div align=center>
<img src="https://user-images.githubusercontent.com/44863827/201052605-78fdd0e9-a109-4894-b3bf-a5f9eaabbdd2.png">
</div>

## OBJECTIVE

The script performs combination of hazard and exposure geodata from global datasets according to user input and settings, and returns a risk score in the form of Expected Annual Impact (EAI) for baseline (reference period). 
The spatial information about hazard and exposure is first combined at the grid level, then the total risk estimate is calculated at ADM boundary level. This represents the disaster risk historical baseline.
The output is exported in form of tables, statistics, charts (excel format) and maps (geopackage).

## SCRIPT OVERVIEW

- Script runs on one country, one hazard at time to keep the calculation time manageable.
- The analysis is carried at the resolution of the exposure layer. E.g. when using Worldpop exposure layer, it is 100x100 meters.
- User input is required to define country, exposure layer, and settings.
- Settings affect how the processing runs (min theshold).
- The core of the analysis is raster calculation, combinining exposure and hazard value through an impact function.
- The information is then aggregated at ADM level using zonal statistic.
- The expected annual impact (EAI) is computed by multiplying the impact value with its exceedence frequency (1/RPi - 1/RPj) depending on the scenario. The exceedance frequency curve (EFC) is plotted.
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

### SETUP
- Load required libraries

### USER INPUT
- Country of interest (1): Name or ISO code 
- Exposure category (1): a) population; b) land cover 

### SETTINGS (DEFAULTS can be changed)
- Min Hazard threshold: data below this threshold are being ignored

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

## DATA PROCESSING

- LOOP over each hazard RPi layers:
  - Filter hazard layer according to settings (min and max thresholds) for each RPi -> `RPi_filtered`
  - Transform hazard intensity value into impact factor using specific hazard impact function or table: `RPi_filtered` -> `RP_IF`
  - RPi_IF is multiplied with the exposure layer to obtain expected impact: `RPi_IF` -> `RPi_exp_imp`
  - Perform zonal statistic (SUM) for each ADMi unit over every RPi_exp_imp -> `table [ADMi_NAME;RPi_exp_imp]`
    <br> e.g. `[ADM2_NAME;RP10_exp_imp;RP100_exp_imp;RP1000_exp_imp]`<br><br>

  <div align=center>
  <img src="https://user-images.githubusercontent.com/44863827/201050148-5aa6ad10-44b2-480f-9bef-51c3703d0e33.png">
  </div>

- Calculate EAI
  - Calculate the exceedance frequency for each RPi -> `RPi_ef = (1/RPi - 1/RPj)` where `j` is the next RP in the serie.
    Example using 3 scenarios: RP 10, 100, and 1000 years. Then: `RP10_ef = (1/10 - 1/100) = 0.09`
  - Multiply impact on exposure for each scenario `(RPi_Exp_imp)` with its exceedence frequency `(RPi_ef)` -> `RPi_Exp_EAI`
  - Sum all `RPi_exp_EAI` columns for each ADMi -> `table [ADMi;Exp_EAI]`

	| RP | Freq | Exceedance freq | Impact | EAI |
	|:---:|:---:|:---:|:---:|:---:|
	| 10 | 0.100 | 0.09 | 193 | 17 |
	| 100 | 0.010 | 0.009 | 1,210 | 11 |
	| 1000 | 0.001 | 0.001 | 3,034 | 3 |
	| Total |   |   |   | **31** |
  
  - Plot Exceedance Frequency Curve. Example:<br>
    ![immagine](https://user-images.githubusercontent.com/44863827/201049813-008d5fbc-3195-4289-ba18-34a126fe434e.png)
  - Perform zonal statistic of Tot_Exp using ADMi -> `[ADMi;ADMi_Exp;Exp_EAI]` in order to calculate `Exp_EAI% = Exp_EAI/ADMi_Exp` -> `[ADMi;ADMi_Exp;Exp_EAI;Exp_EAI%]`

## PREVIEW RESULTS
- Plot map of ADMi_EAI and related tables/Charts

  <div align=center>
  <table><tr><td width="45%"><img src="https://user-images.githubusercontent.com/44863827/201054765-5a1ce2c9-0bde-4e98-80ce-ee30ccefc4e2.png"></td>
	  <td><img src="https://user-images.githubusercontent.com/44863827/201055152-28482f07-7215-4b09-b3c2-397381d516af.png"></td></tr></table>
  </div>

## EXPORT RESULTS
- Export geodata output as gpkg and tables.

--------------------------------------

# EQUIVALENT PROCESSING IN QGIS

The following display equivalent spatial analytics steps performed by the script by using QGIS (well known, free geospatial tool).

## DATA MANAGEMENT

- Load map data: ADM units (3 layers), hazard (one or as many layers as RP scenarios) and exposure (population map, land cover, etc).
  In this example, we use FATHOM river flood data (light blue) and WorldPop2020-constrained-US_adjusted population data (green to purple).

  <img width=50% src="https://user-images.githubusercontent.com/44863827/151433893-76299364-f416-487f-a3e1-acf082d8b137.png">

- (optional) assign symbology for each one to print out readable maps. Consider min and max hazard thresholds and classes when building symbology.

  <img width=50% src="https://user-images.githubusercontent.com/44863827/151356576-7f56d2a6-4314-4bcb-9727-377bd032ac54.png">

- Apply min threshold for hazard, if required. In the example, we consider values < 0.5 m as non-impacting due to defence standards, and values > 10 m as part of the water body. Repeat this step for multiple RPs.

  <img width=60% src="https://user-images.githubusercontent.com/44863827/151812298-25d14746-7d79-4d6e-8b67-3751a29233db.png">

## ANALYTICAL APPROACH 

In this scenario, a mathematical (quantitative) relationship is available to link physical hazard intensity and impact magnitude over built-up asset.

- `Raster calculator`: tranlate the hazard map (one layer or multiple RP) into impact factor map.
  In this example, the average flood damage curve for Asia (JRC 2017) is used to aproximate an impact on built-up land cover.
  A polynomial function is fitted to the curve (R2= 0.99), where x is the hazard metric (water depth); the max damage is set to 1:
  
  `y= MIN(1, 0.00723 \* x^3 - 0.1 \* x^2 + 0.506 \* x)`
  
  <img width=50% src="https://user-images.githubusercontent.com/44863827/151544290-1306bda1-30a4-4729-9e4d-c025cf4f6f2e.png">
  
  The resulting impact factor layers RPi has values ranging 0-1.
  
  <img width=37% src="https://user-images.githubusercontent.com/44863827/151798346-121dae76-1004-468d-9ec2-8f89d056ceed.png"> <img width=40% src="https://user-images.githubusercontent.com/44863827/151381602-319c426f-273d-482c-ace2-059b6375b4b3.png">

- `Raster calculator`: multiply the impact factor map with the exposure map. The resulting layer RPi_Pop represent the share of people impacted under RP10.

  <img width=37% src="https://user-images.githubusercontent.com/44863827/151382232-4a48272a-6615-4a75-96d8-405c5d4d14e1.png"> <img width=40% src="https://user-images.githubusercontent.com/44863827/151381319-6a9b3fe9-f7f2-4dcd-b497-91bfcaac1c03.png">

- `Zonal statistic`: select "sum" criteria to aggregate impacted built-up at ADM3 level. A new column "RP10_exp_sum" is added to ADM3 layer: plot it to desired simbology.

  <img width=35% src="https://user-images.githubusercontent.com/44863827/151384000-0a71e054-49a8-414b-bf3e-77432b135543.png">  <img width=45% src="https://user-images.githubusercontent.com/44863827/151402320-3ed9a157-59cd-4a5d-8209-312e9aaf0b7c.png">

  In order to express the value as % of total, we need the total built-up for each ADM3 unit.
  
- `Zonal statistic`: select "sum" criteria on the Built-up layer of choice.

If the hazard is represented by **one layer**, it is assumed to represent the Expected Annual Impact (EAI).

Otherwise, this procedure is repeated for **each RP layer**, and then the EAI is computed as described in the following steps.

- Once reapeted over all RP layers, the ADM3 layer used to perform zonal statistic will include all the required information to calculate EAI and EAI%.
  The impact for each column is multiplied by the year frequency of the return period (RPf), calculated as RPf = 1/RP or, in the case where the set includes RP 1 year, as:
  RPf = 1 - EXP(-1/RP). Then, the column are summed up to a total, representing EAI.
    
  <img width=50% src="https://user-images.githubusercontent.com/44863827/151416889-8adafa0c-584b-4505-8185-6ee46c7f1bfe.png">    

- Create a new column and calculate the percentage of expected annually impacted built-up over total.

- Plot results as map: absolute numbers and percentage over total values for ADM level.

  <img width=60% src="https://user-images.githubusercontent.com/44863827/151826096-43510935-efb7-40c4-a2af-82f7c4c29564.png"> <img width=60% src="https://user-images.githubusercontent.com/44863827/151825526-14ba5f89-725d-4ee9-9943-f9bc7a91e225.png">
 
- Results can be furtherly aggregated for ADM2 and ADM1 levels by creating a new column ADM2_EAI ADM1_EAI and summing all EAI using ADM2_code and ADM1_code as index.
