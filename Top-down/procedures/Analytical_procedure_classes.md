# ANALYTICAL APPROACH = Expected Annual Exposure (EAE) 

## OBJECTIVE

The script performs combination of hazard and exposure geodata from global datasets according to user input and settings, and returns a risk score in the form of Expected Annual Exposure (EAE) for the baseline (reference period). 

The "classes" approach simply split the hazard intensity layer into classes and, for ach one, calculates the toal exposure for the selected category. 
For example, flood hazard over agriculture is measured in terms of hectars of land falling within different intervals of water depth.
Note that Minimum threshold is deactivated/ignored for this approach.

The spatial information about hazard and exposure is first collected at the grid level, the output is then aggregated at ADM2 boundary level to combine Vulnerability scores and calculate risk estimate. This represents the disaster risk historical baseline.

The output is exported in form of tables, statistics, charts (excel format) and maps (geopackage).

## SCRIPT OVERVIEW

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

## SCRIPT STRUCTURE

- SETUP: environment and libraries
- USER INPUT: required
- SETTINGS: default parameters can be changed by user
- DATA MANAGEMENT: global datasets are loaded according to user input
- DATA PROCESSING: datasets are processed according to settings
- PREVIEW RESULTS: plot tables and maps
- EXPORT RESULTS: results are exported as excel according to template

## PRE-REQUISITES (OFFLINE)

- Anaconda and python installed > NOT IF if we use jupyter desktop! Autoinstaller!


## SCRIPT STEP-BY-STEP

### SETUP

- Load required libraries
- Load HazardStats script (zonal statistics)

### USER INPUT

- Country of interest (1): Name or ISO code 
- Exposure category (1): a) population; b) land cover 

Optional:
- Future time horizon: 2050, 2080 
- RCP scenario: RCP 2.6, 4.5, 6.5, 8.5 

### SETTINGS (DEFAULTS can be changed)

- Criteria for aggregation: a) MAX; b) Mean
- Number of classes: 5 (3 to 10)
- Min Hazard threshold: data below this threshold are being ignored
- Max Hazard threshod: data above this threshold are considered as the threshold value (max expected impact)

### SUMMARY OUTPUT SETTINGS

- Display input and settings, preview classes intervals as table:

	- Country: Nepal (NPL)
	- Exposure: Population
	- Values aggregation criteria: Max
	- Output classes: Class value indicates the beginning of the class interval. Last class goes to infinite.
	<img width=200 src="https://user-images.githubusercontent.com/44863827/156603360-dabc7da2-52c8-4ed2-be07-bd2a4927af16.png">

------------------------------------------

## DATA MANAGEMENT - BASELINE

- Load country boundaries from ADM_012.gpkg (world boundaries at 3 levels). Includes ISO3 code related to country name.
	- The whole gpkg is 1.5 Gb, for now I have a SAR-only version loaded. Would be good to have a way to get only the required ISO from main gpkg.
	- Alternatively, we could API-request ADM via https://www.geoboundaries.org/api.html, however the quality of the layers is mixed!
          Some mismatch among different levels boundaries, different years update, etc.

- Load population from WorldPop API according to ISO3 code:

	https://www.worldpop.org/rest/data/pop/wpgp?iso3=NPL

    returns a Json that includes the url of data:

	https://data.worldpop.org/GIS/Population/Global_2000_2020/2020/NPL/npl_ppp_2020.tif
	
    This is a 100m grid representing the total popuation estimated in each cell.

- Load hazard data from drive (for prototype). Most hazard data consist of 3 grids, each representing one event frequency (return period).


## DATA PROCESSING - BASELINE

- LOOP over all hazard RPs:

  - Classify hazard layer according to settings: min and max thresholds, number of classes -> RPi_classes (multiband raster)
  - Each class of RP is used to mask the population layer -> RPi_class_pop (multiband raster)
  - Perform zonal statistic (SUM) for each ADM2 unit over RPi_class_pop -> table (ADM2_NAME;RPi_C1_p;RPi_C2_p;...RPi_Ci_p)
  - Calculate RPi_C1_p * V-factor (previously embedded in ADM2 layer) -> table (ADM2_NAME;RPi_C1_p_impact;RPi_C2_p_impact;...RPi_Ci_p_impact)
  - Sum all RPi_Ci_p_impact columns for each ADM2 row -> table [ADM2;RP100_tot_p_impact]

- END LOOP; all RPs combined -> table [ADM2;RP10_impact;RP100_impact_RP1000_impact]

- Multiply RPi_impact by RP_P (1-EXP(-1/RP)) -> table [ADM2;RP10_EAI;RP100_EAI;RP1000_EAI]

- Sum all RPi_EAI columns for each ADM2: table [ADM2;Pop_EAI]

- Aggregate at ADM1 level according to criteria (Max or Mean)

## PREVIEW RESULTS - BASELINE

- Plot map of ADM2/ADM1
- Plot tables/Charts

## EXPORT RESULTS - BASELINE

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

- Raster calculator: split the layer (one layer or multiple RP) into multiple impact classes. Repeat the changing the interval values for each class. 

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
