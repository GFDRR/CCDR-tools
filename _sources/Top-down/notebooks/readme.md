# ANALYTICAL NOTEBOOKS

For detailed explanation of the analytical workflow, please refer to [Procedures](../procedures/).


## SCRIPT SETUP
Note: at this stage you need to manually download all the notebooks in this folder and create your python environment as from instructions below.
This could be further improved in the form of a self-installing desktop app using [Voila](https://github.com/voila-dashboards/voila).

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

# THE ENTRIES BELOW DO NOT NEED TO BE EDITED
# Location to store results of analyses
OUTPUT_DIR = ${DATA_DIR}/RSK/

# Location to store downloaded rasters and other data
# for the analysis notebooks
CACHE_DIR = ${DATA_DIR}/cache/
```

- Navigate to your working directory: `cd <Your work directory>`
- Run `jupyter notebook`
- Select [CCDR.ipynb](https://github.com/GFDRR/CCDR-tools/blob/main/Top-down/notebooks/CCDR.ipynb) and chose the hazard to analyse.

  <img width=500 src="https://user-images.githubusercontent.com/44863827/170250738-03ad2f05-a128-4d84-ab27-01dcec54c4e4.png">
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

