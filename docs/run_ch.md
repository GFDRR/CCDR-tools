# Custom Hazard Analytics

## Input data management

This script is meant for custom input from the user on all three risk components. It can still fetch national and sub-national boundaries from the [WB ArcGIS repository](https://services.arcgis.com/iQ1dY19aHwbSDYIF/ArcGIS/rest/services/World_Bank_Global_Administrative_Divisions_VIEW/FeatureServer).

The [**exposure data**](global-exposure.md) and the [**hazard data**](global-hazard.md) selected by the user need to be manually downloaded and placed in the respecive folders; in case of tiled data, use the [pre-processing script](https://github.com/GFDRR/CCDR-tools/blob/main/tools/code/F3/) to merge those into country-sized data. Each dataset is expected as a raster file (`.tif`).<br>

Example:

  ```
  Work dir/
   - GUI.ipynb		Place the notebooks and related files in the main work directory
   - common.py
   - ...
   - Data/
     - HZD/country_hazard.tif				Hazard layers
     - EXP/country_exposure.tif				Exposure layers
     - RSK/						Output directory
  ```

  ```{caution}
  All spatial data must use the same CRS: `EPSG 4326` (WGS 84)
  ```
<hr>

## Running the analysis

- Select the country first. Sub-national boundaries for level 1 and 2 can be fetched automatically. Else, you can load custom boundaries as geopackage (WGS 84). You will need to specify the field to be used to run zonal statistics, and related label name (e.g. ADM3_PCODE and ADM3_EN).
    ```{figure} images/GUI_F3_country.png
    ---
    width: 100%
    align: center
    ---
    ```
- Move to Hazard tab: select the hazard process, the minimum hazard intensity threshold, the time period and climate scenario. Select one or more Return Periods (CTRL+Click / drag mouse).
    ```{figure} images/GUI_F3_hzd.png
    ---
    width: 100%
    align: center
    ---
    ```
- Select one or more Exposure categories (CTRL+Click / drag mouse). You can select a custom exposure layer for each selected category (.tif raster, WGS 84).
    ```{figure} images/GUI_F3_exp.png
    ---
    width: 100%
    align: center
    ---
    ```
- Select the approach to use for the analysis:
  - When using "function", the best impact function is selected for the selected country and exposure categories.
  - When using "classes", hazard intensity thresholds must be specified by the user.
    ```{figure} images/GUI_F3_vln.png
    ---
    width: 100%
    align: center
    ---
    ```
- Check "Preview results" to generate map and charts output in the GUI.

```{figure} images/GUI_F3_rsk.png
---
width: 100%
align: center
---
```
