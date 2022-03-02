# CCDR ANALYTICAL NOTEBOOKS - TIER 1

## Multi-hazard risk screening based on global/regional datasets


--------------------------------------

# SCRIPT SETUP
Note: this will be improved with script finalisation! Hopefully in the form of a self-installing app.

- The script requires python3 - conda or mamba are encouraged
- Create a new environment named CCDR based on win_env.yml o linux_env.yml depending on your operating system.
	`conda create --name CCDR --file <dir/win_env.yml>`
	`activate CCDR`

- Navigate to your working directory: `cd <paste directory>`
- Run `jupyter notebook`

- The script expects input data folders to be structured as:

```
Root/
 - Hazrd_Notebook.ipynb
 - common.py
 - .env
 - Data/
   - ADM	Administrative unit layer for each country as geopackage ISO_ADM.gpkg
   - HZD	Hazard layers (rasters)
   - EXP	Exposure layers - Population (count), Built-up (ratio or binary), Agriculture (ratio or binary)
   - RSK	Output directory
```

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

--------------------------------------

# EQUIVALENT PROCESSING IN QGIS

The following display the same processing spatial performed by the script by using QGIS (well known, free geospatial tool).

### DATA MANAGEMENT

- Load map data: ADM units (3 layers), hazard (one or as many layers as RP scenarios) and exposure (population map, land cover, etc).
  In this example, we use FATHOM river flood data (light blue) and WorldPop2020-constrained-US_adjusted population data (green to purple).

  <img width=50% src="https://user-images.githubusercontent.com/44863827/151433893-76299364-f416-487f-a3e1-acf082d8b137.png">

- (optional) assign symbology for each one to print out readable maps. Consider min and max hazard thresholds and classes when building symbology.

  <img width=50% src="https://user-images.githubusercontent.com/44863827/151356576-7f56d2a6-4314-4bcb-9727-377bd032ac54.png">

- Apply min threshold for hazard, if required. In the example, we consider values < 0.5 m as non-impacting due to defence standards, and values > 10 m as part of the water body. Repeat this step for multiple RPs.

  <img width=60% src="https://user-images.githubusercontent.com/44863827/151812298-25d14746-7d79-4d6e-8b67-3751a29233db.png">

### OPTION 1 - USING A IMPACT CURVE / FUNCTION

In this scenario, a mathematical (quantitative) relationship is available to link physical hazard intensity and impact magnitude.

- Raster calculator: tranlate the hazard map (one layer or multiple RP) into impact factor map.
  In this example, the average flood damage curve for Asia is used to aproximate an impact on population, although being developed for structural asset.
  A polynomial function is fitted to the curve (R2= 0.99), where x is the hazard metric (water depth); the max damage is set to 1:
  y= MIN(1, 0.00723 \* x^3 - 0.1 \* x^2 + 0.506 \* x)
  
  <img width=50% src="https://user-images.githubusercontent.com/44863827/151544290-1306bda1-30a4-4729-9e4d-c025cf4f6f2e.png">
  
  The resulting impact factor layers RPi has values ranging 0-1.
  
  <img width=37% src="https://user-images.githubusercontent.com/44863827/151798346-121dae76-1004-468d-9ec2-8f89d056ceed.png"> <img width=40% src="https://user-images.githubusercontent.com/44863827/151381602-319c426f-273d-482c-ace2-059b6375b4b3.png">

- Raster calculator: multiply the impact factor map with the exposure map. The resulting layer RPi_Pop represent the share of people impacted under RP10.

  <img width=37% src="https://user-images.githubusercontent.com/44863827/151382232-4a48272a-6615-4a75-96d8-405c5d4d14e1.png"> <img width=40% src="https://user-images.githubusercontent.com/44863827/151381319-6a9b3fe9-f7f2-4dcd-b497-91bfcaac1c03.png">

- Zonal statistic: select "sum" criteria to aggregate impacted population at ADM3 level. A new column "RP10_pop_sum" is added to ADM3 layer: plot it to desired simbology.

  <img width=35% src="https://user-images.githubusercontent.com/44863827/151384000-0a71e054-49a8-414b-bf3e-77432b135543.png">  <img width=45% src="https://user-images.githubusercontent.com/44863827/151402320-3ed9a157-59cd-4a5d-8209-312e9aaf0b7c.png">

  In order to express the value as % of total, we need the total population for each ADM3 unit.
  
- Zonal statistic: select "sum" criteria on the Population layer of choice.

If the hazard is represented by **one layer**, it is assumed to represent the Expected Annual Impact (EAI).

Otherwise, this procedure is repeated for **each RP layer**, and then the EAI is computed as described in the following steps.

- Once reapeted over all RP layers, the ADM3 layer used to perform zonal statistic will include all the required information to calculate EAI and EAI%.
  The impact for each column is multiplied by the year frequency of the return period (RPf), calculated as RPf = 1/RP or, in the case where the set includes RP 1 year, as:
  RPf = 1 - EXP(-1/RP). Then, the column are summed up to a total, representing EAI.
    
  <img width=50% src="https://user-images.githubusercontent.com/44863827/151416889-8adafa0c-584b-4505-8185-6ee46c7f1bfe.png">    

- Create a new column and calculate the percentage of expected annually impacted people over total population.

- Plot results: absolute numbers and percentage over ADM3 total population.

  <img width=60% src="https://user-images.githubusercontent.com/44863827/151826096-43510935-efb7-40c4-a2af-82f7c4c29564.png"> <img width=60% src="https://user-images.githubusercontent.com/44863827/151825526-14ba5f89-725d-4ee9-9943-f9bc7a91e225.png">
 
- Results can be furtherly aggregated for ADM2 and ADM1 levels by creating a new column ADM2_EAI ADM1_EAI and summing all EAI using ADM2_code and ADM1_code as index.

-------------------------------

### OPTION 2 - USING IMPACT CATEGORIES CLASSIFICATION

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

