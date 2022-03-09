# CCDR ANALYTICAL NOTEBOOKS
## Multi-hazard risk screening based on global/regional datasets

--------------------------------------

## OVERVIEW
This is an open tool for risk screening based on globally-avaialble datasets. 

The ‘top-down’ approach offers analytical notebooks allowing non-experts to perform comprehensive, multi-hazard risk screening using regionally available and comparable datasets. The work under this tier is characterized by: 

 - Global and regional-scale data inputs 
 - User-friendly, and easily interpretable tools and outputs
 - Some degree of customisation, but ensuring transferability and comparability between countries 

Analysis runs over high resolution exposure data (90 m) and is then aggregated at the required administrative level. This approach provides sub-national mapping of natural hazards, exposure and risk,  which can inform policy and targeted interventions. Risk is calculated independently for each individual hazard.

--------------------------------------

## SCRIPT SETUP
Note: this will be improved with script finalisation! Hopefully in the form of a self-installing desktop app using [Voila](https://github.com/voila-dashboards/voila).

### Environment and libraries
- The script requires python3 - conda or mamba are encouraged
- Create a new environment named CCDR based on win_env.yml o linux_env.yml depending on your operating system.
  In Anaconda cmd prompt:

	`conda create --name CCDR --file <dir/win_env.yml>`
	
	`activate CCDR`

Edit the `.env` file inside the notebook directories to specify the working directory:

```
# Environment variables for the CCDR Climate and Disasater Risk analysis notebooks

# Fill the below with the location of data files
# Use absolute paths with forward slashes ("/"), and keep the trailing slash
DATA_DIR = ""

# Location to store results of analyses
OUTPUT_DIR = ${DATA_DIR}/RSK/

# Location to store downloaded rasters and other data
# for the analysis notebooks
CACHE_DIR = ${DATA_DIR}/cache/
```

- Navigate to your working directory: `cd <Your work directory>`
- Run `jupyter notebook`
- Execute all cells. The last one will present the user interface:

<img width=500 src="https://user-images.githubusercontent.com/44863827/156407683-c5613196-53bc-4ee5-81b7-d94b4fdbf295.png">

--------------------------------------

### Expected directories and data format

- The script expects input data folders to be structured as:

```
Work dir/
 - Hazard.ipynb
 - common.py
 - .env
 - Data/
   - ADM	Administrative unit layer for each country
   - HZD	Hazard layers
   - EXP	Exposure layers - Population (count), Built-up (ratio or binary), Agriculture (ratio or binary)
   - RSK	Output directory
```

- **ADMINISTRATIVE** boundaries are provided as geopackage files named as `ISO`_ADM.gpkg (exampe `NPL_ADM.gpkg`) made of multiple layers, up to ADM level 3:

```
- ISO_ADM
  - ADM0
  - ADM1
  - ADM2
  - ADM3
```
- All spatial data must use CRS `EPSG 4326`
- Each ADM layer should include relative ADMi_CODE and ADMi_NAME across levels to facilitate aggrgation of results:

  - ADM0:

  | ISO3166_a2 | ISO3166_a3 | ADM0_CODE | ADM0_NAME | 
  |---|---|---|---|
  | String(2) | String(3) | Integer | String (20) |
 
  - ADM1

  | ADM0_CODE | ADM0_NAME | ADM1_CODE | ADM1_NAME | 
  |---|---|---|---|
  | Integer | String (20) | Integer | String(20) |

  - ADM2

  | ADM0_CODE | ADM0_NAME | ADM1_CODE | ADM1_NAME | ADM2_CODE | ADM2_NAME | 
  |---|---|---|---|---|---|
  | Integer | String (20) | Integer | String(20) | Integer | String(20) |

  - ADM3
  
  | ADM0_CODE | ADM0_NAME | ADM1_CODE | ADM1_NAME | ADM2_CODE | ADM2_NAME | ADM3_CODE | ADM3_NAME | 
  |---|---|---|---|---|---|---|---|
  | Integer | String (20) | Integer | String(20) | Integer | String(20) | Integer | String(20) |

- **HAZARD** layers are expected as raster files (`.tif`) named as `ISO`_HZD_RPi.tif (exampe for Nepal flood, RP100: `NPL_FL_RP100.tif`). Any resolution should work, but using  resolution below 90m over large countries could cause very long processing and memory cap issues.
- **EXPOSURE** are expected as raster files (`.tif`) named as `ISO`_EXP.tif (exampe for Nepal flood, RP100: `NPL_FL_RP100.tif`). The same suggestion about resolution applies here.

	- Population from Worldpop, 90 m: `ISO`_POP.tif
	- Built-up from World Settlement Footprint or equivalent, 90 m: `ISO`_BUP.tif
	- Agriculture from land cover map, ESA land cover or equivalent, 90 m: `ISO`_AGR.tif

When resampling EXP layers to a lower resolution, it is **strongly recommended** to align the resampled grid to exactly match the hazard grid.

<img width=600 src="https://user-images.githubusercontent.com/44863827/157419284-64e16285-6284-45ba-bc9c-01eab713c2f1.png">

--------------------------------------

# RUNNING THE SCRIPT

Once required input layers have been created according to standards, the script can run.

Select the country of interest, the exposure category and the level of administrative boundaries aggregation.

Note that not all combinations of hazards x exposure are supported; some are not covered by appropriate damage functions or classification. Select the analytical approach accordingly.

![immagine](https://user-images.githubusercontent.com/44863827/156599257-a9f587b4-bcbf-4e6b-9793-6e346945dca5.png)

## ANALYTICAL APPROACH = Impact function
The "function" approach uses a mathematical relationship to calculate impact over exposed categories.
For example, flood hazard impact over population is calculated using a mortality function, while the impact over built-up uses a damage function for buildings.

The functions can be manually edited in the notebook, if a better model is available for the country of interest.

<img width=700 src="https://user-images.githubusercontent.com/44863827/156601011-5b8cf8af-8703-4d2a-8dbf-698b9e132b6f.png">

A minimum threshold can be set to ignore all values below - assuming that all risk is avoided under this threshold.

<img width=400 src="https://user-images.githubusercontent.com/44863827/156601233-8bb33d74-127a-4e60-93a3-0cc683d0efba.png">

A chart of the impact function can be generated in the interface for the selected exposure category.

<img width=400 src="https://user-images.githubusercontent.com/44863827/156601989-4997c63c-8c2a-4ce4-b6f9-bb7bb0506799.png">

If you want to inspect all steps of the processing, you can select the option to export all by-products as tiff files:

- [X] Export Intermediate rasters

***>>> RUN ANALYSIS <<<***

Once the run finishes, results are exported as geospatial data (.gpkg) and table (.csv).

By selecting

- [X] Preview results

A map will be generated at the end of the run, using a simple simbology.

<img width=700 src="https://user-images.githubusercontent.com/44863827/156605538-85af4764-a2cb-4d0f-8046-a59fdcbed50b.png">

The map can be zoomed and inspected with the pointer to show all the values in the table.

<img width=500 src="https://user-images.githubusercontent.com/44863827/156605784-b80e4ba8-aafd-4316-b9f8-d3657230a1d4.png">

EAI represents the aggregated absolute risk estimate:
 - **Fatalities** when considering impact over population;
 - **Hectars [ha] of built-up destroyed** when considering impact over built-up.

---------------

## ANALYTICAL APPROACH = Exposure classification

The "classes" approach simply split the hazard intensity layer into classes and, for ach one, calculates the toal exposure for the selected category. 
For example, flood hazard over agriculture is measured in terms of hectars of land falling within different intervals of water depth.
Note that Minimum threshold is deactivated.

<img width=400 src="https://user-images.githubusercontent.com/44863827/156603360-dabc7da2-52c8-4ed2-be07-bd2a4927af16.png">

When the run finishes, geospatial data are exported as .gpkg and .csv.

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

### ANALYTICAL APPROACH 1 - USING A IMPACT CURVE / FUNCTION

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

-------------------------------

### ANALYTICAL APPROACH 2 - USING IMPACT CATEGORIES CLASSIFICATION

In this scenario, the physical hazard intensity is ranked in qualitative classes of impact magnitude. This is the case when no impact function is available for the category at risk, but a classification of impact by hazard thresholds is possible. Starting from the thresholded layer, we split the hazard intensity (water depth, as in previouse example) into 6 classes, each representing an interval of 0.5 m - except the last one, the includes all values > MAX damage ratio. Then, we extract the total population located within each hazard class for each ADM3 unit into an excel table for further analytics to be applied.

Water depth classes:
| min | Max | 
|-----|---|
| 0.5 | 1 |
| 1 | 1.5 |
| 1.5 | 2 |
| 2 | 2.5 |
| 2.5 | 3 |
| 3 | 10 |

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

