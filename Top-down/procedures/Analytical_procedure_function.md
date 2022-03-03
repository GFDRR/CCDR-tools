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
