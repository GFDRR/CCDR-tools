# Tools setup

### Expected directories and input format

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

  - **ADM0**

  | ISO3166_a2 | ISO3166_a3 | ADM0_CODE | ADM0_NAME | 
  |---|---|---|---|
  | String(2) | String(3) | Integer | String (20) |
 
  - **ADM1**

  | ADM0_CODE | ADM0_NAME | ADM1_CODE | ADM1_NAME | 
  |---|---|---|---|
  | Integer | String (20) | Integer | String(20) |

  - **ADM2**

  | ADM0_CODE | ADM0_NAME | ADM1_CODE | ADM1_NAME | ADM2_CODE | ADM2_NAME | 
  |---|---|---|---|---|---|
  | Integer | String (20) | Integer | String(20) | Integer | String(20) |

  - **ADM3**
  
  | ADM0_CODE | ADM0_NAME | ADM1_CODE | ADM1_NAME | ADM2_CODE | ADM2_NAME | ADM3_CODE | ADM3_NAME | 
  |---|---|---|---|---|---|---|---|
  | Integer | String (20) | Integer | String(20) | Integer | String(20) | Integer | String(20) |

- **HAZARD** layers are expected as raster files (`.tif`) named as `ISO`_HZD_RPi.tif (exampe for Nepal flood, RP100: `NPL_FL_RP100.tif`). Any resolution should work, but using  resolution below 90m over large countries could cause very long processing and memory cap issues.

- **EXPOSURE** are expected as raster files (`.tif`) named as `ISO`_EXP.tif (exampe for Nepal flood, RP100: `NPL_FL_RP100.tif`). The same suggestion about resolution applies here.

	- Population from GHSL, 90 m: `ISO`_POP.tif
	- Built-up from World Settlement Footprint or equivalent, 90 m: `ISO`_BUP.tif
	- Agriculture from land cover map, ESA land cover or equivalent, 90 m: `ISO`_AGR.tif

When resampling EXP layers to a lower resolution, it is **strongly recommended** to align the resampled grid to exactly match the hazard grid.

<img width=600 src="https://user-images.githubusercontent.com/44863827/157419284-64e16285-6284-45ba-bc9c-01eab713c2f1.png">

<hr>

## Environment and libraries
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

```{figure} images/ccdr-nb.png
---
align: center
---
Starting page for the CCDR python notebooks
```

- Execute all cells. The last one will present the user interface:

```{figure} images/ccdr-nb_settings.png
---
align: center
---
Settings from one of the python notebooks
```