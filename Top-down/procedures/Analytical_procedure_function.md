# OBJECTIVE

The script performs combination of hazard and exposure geodata from global datasets according to user input and settings, and returns a risk score in the form of Expected Annual Impact (EAI) for baseline (reference period). 
The spatial information about hazard and exposure is first collected at the grid level, the output is then aggregated at ADM2 boundary level to combine Vulnerability scores and calculate risk estimate. This represents the disaster risk historical baseline.

The output is exported in form of tables, statistics, charts (excel format) and maps (geopackage).


# SCRIPT OVERVIEW

- Each script is hazard specific, because each hazard has its own metrics and thresholds; putting all in one script could be confusing for the user.
- Script runs on one country at time to keep the calculation time manageable.
- The analysis is carried at the resolution of the exposure layer. For prototype, worldpop is 100m.
- User input is required to define country, exposure layer, and settings.
- Settings affect how the processing runs (criteria, thesholds, number of classes).
- The core of the analysis is zonal statistics: how much population falls in each class of hazard.
- The information is aggregated at ADM2 level and combined with Vulnerability scores according to an algo (tbd) to produce impact score for each RP.
- The exceedance frequency curve (EFC) is built and plotted by interpolation of these 3 points.
- The expected annual impact (EAI) is computed by multiplying the impact score with the frequency (1/RP) of the events and sum the multiplied impact.
- The table results are exported in excel format.
- The vector rsults are exported in gpkg format.


# SCRIPT STRUCTURE

- SETUP: environment and libraries
- USER INPUT: required
- SETTINGS: default parameters can be changed by user
- DATA MANAGEMENT: global datasets are loaded according to user input
- DATA PROCESSING: datasets are processed according to settings
- PREVIEW RESULTS: plot tables and maps
- EXPORT RESULTS: results are exported as excel according to template

# PRE-REQUISITES (OFFLINE)

- Anaconda and python installed > Possibly we move to jupyter desktop Autoinstaller
- Create environment from ccdr_analytics.yml

# SCRIPT STEP-BY-STEP

## SETUP

- Load required libraries

## USER INPUT

- Country of interest (1): Name or ISO code 
- Exposure category (1): a) population; b) land cover 

## SETTINGS (DEFAULTS can be changed)

- Criteria for aggregation: a) MAX; b) Mean
- Min Hazard threshold: data below this threshold are being ignored
- Max Hazard threshod: data above this threshold are considered as the threshold value (max expected impact)

## SUMMARY OUTPUT SETTINGS

- Display input and settings:

	- Country: Nepal (NPL)
	- Exposure: Population
	- Values aggregation criteria: Max

------------------------------------------

## DATA MANAGEMENT

- Load country boundaries from ADM_012.gpkg (world boundaries at 3 levels). Includes ISO3 code related to country name.
	- The whole gpkg is 1.5 Gb, for now I have a SAR-only version loaded. Would be good to have a way to get only the required ISO from main gpkg.
	- Alternatively, we could API-request ADM via https://www.geoboundaries.org/api.html, however the quality of the layers is mixed!
          Some mismatch among different levels boundaries, different years update, etc.

- Load population from WorldPop API according to ISO3 code:

	https://www.worldpop.org/rest/data/pop/wpgp?iso3=NPL

    returns a Json that includes the url of data:

	https://data.worldpop.org/GIS/Population/Global_2000_2020/2020/NPL/npl_ppp_2020.tif
	
    This is a 100m grid representing the total popuation estimated in each cell.

- Load hazard data from drive (for prototype). Most hazard data consist of 3 raster layers, each representing one event frequency scenario (return period).

- Plot ADM and Pop data as map [if easy]

## DATA PROCESSING

- LOOP over all hazard RP layers:
  - Filter hazard layer according to settings (min and max thresholds) -> RP
  - Transform hazard intensity value into impact factor using specific hazard impact function or table -> RPi
  - RPi is multiplied as mask with the population layer -> RPi_pop
  - Perform zonal statistic (SUM) for each ADM2 unit over RPi_pop -> table (ADM2_NAME;RPi_pop)

- END LOOP; all RPs combined -> table [ADM2;RP10i_pop;RP100i_pop;RP1000i_pop]

- Multiply RPi by RP frequency, RPf = 1/RP (or RPf = 1-EXP(-1/RP) if RP = 1) -> table [ADM2;RP10_EAI;RP100_EAI;RP1000_EAI]

- Sum all RPi_EAI columns for each ADM2: table [ADM2;Pop_EAI]

- Perform zonal statistic of Tot_Pop using ADM2 -> [ADM2;ADM2_Pop;Pop_EAI]

- Calculate Pop_EAI% = Pop_EAI/ADM2_Pop -> [ADM2;ADM2_Pop;Pop_EAI;Pop_EAI%]

- Aggregate at ADM1 level according to criteria (Max or Mean)

## PREVIEW RESULTS

- Plot map of ADM2/ADM1
- Plot tables/Charts

## EXPORT RESULTS

- Export tables and charts as excel
- Export ADM2/ADM1/ADM0 with joined values as gpkg

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
