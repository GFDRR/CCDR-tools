# Tropical Cyclone Analytics

Based on [**STORM v4**](https://data.4tu.nl/datasets/0ea98bdd-5772-4da8-ae97-99735e891aff/4) (2023) hazard data as max wind spead (m/s) by Return Period scenario.
1. Exposure by hazard thresholds on population, built-up and agricultural area<br>2. Expected Annual Impact estimates on built-up area using regional-specific damage curves from [**CLIMADA**](https://nhess.copernicus.org/articles/21/393/2021/).

## Input data management

The script fetches default data automatically. This includes:

- National and sub-national boundaries from the [WB ArcGIS repository](https://services.arcgis.com/iQ1dY19aHwbSDYIF/ArcGIS/rest/services/World_Bank_Global_Administrative_Divisions_VIEW/FeatureServer).
- Population data from WorldPop
- Built-up data from WSF 2019
- Land-cover (agriculture) data from ESA WorldCover

Default exposure datasets can be overridden by placing custom datasets in the EXP folder and pointing at those file in the interface.

The [**STORM v4 global dataset**](https://github.com/GFDRR/CCDR-tools/tree/5cf98929c985d5c21477168fbea7b0f48c8f03c0/tools/data/HZD/GLB/STORM) is available for download.<br>

Set the folders as: 

  ```
  Work dir/
   - GUI.ipynb		Place the notebooks and related files in the main work directory
   - common.py
   - ...
   - Data/
     - HZD/GLB/STORM/2020	  	                  Hazard layers (baseline)
     - HZD/GLB/STORM/2050	  	                  Hazard layers (future)
     - EXP/		                                  Exposure layers
     - RSK/		                                  Output directory
  ```
<hr>

## Running the analysis

- Select the country first. The country must be located within the hazard extent (tropics) for the analysis to start. 
Sub-national boundaries for level 1 and 2 can be fetched automatically. Else, you can load custom boundaries as geopackage (WGS 84). You will need to specify the field to be used to run zonal statistics, and related label name (e.g. ADM3_PCODE and ADM3_EN).
    ```{figure} images/GUI_TC_country.png
    ---
    width: 100%
    align: center
    ---
    ```
- Move to Hazard tab: select the hazard process, the minimum hazard intensity threshold, the time period and climate scenario. Select one or more Return Periods (CTRL+Click / drag mouse).
    ```{figure} images/GUI_TC_hzd.png
    ---
    width: 50%
    align: center
    ---
    ```
- Select one or more Exposure categories (CTRL+Click / drag mouse). You can select a custom exposure layer for each selected category (.tif raster, WGS 84).
    ```{figure} images/GUI_TC_exp.png
    ---
    width: 50%
    align: center
    ---
    ```
- Select the approach to use for the analysis:
  - When using "function", the best impact function is selected for the selected country. Only built-up damage functions are available for wind impact.
  - When using "classes", hazard intensity thresholds must be specified by the user.

- Check "Preview results" to generate map and charts output in the GUI.

```{figure} images/GUI_TC_rsk.png
---
width: 100%
align: center
---
```