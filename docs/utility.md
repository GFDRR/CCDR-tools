# Utilities
Additional tools to help collect, view and process risk data.

(merge_tiles)=
## Merge tiles
Large raster datasets often comes as a collection of regular tiles.
In order to run the raster analysis offered in our tools, they often need to be merged into one file.
The function is provided as [**jupyter notebook**](../tools/utility/merge_tiles/Merge_tiles.ipynb) you can download and run on your python environment.

(fetch_wsf19)=
## Fetch WSF 2019 and resample as 100 m
WSF offers 10 m binary maps of artificial land cover.
In order to run the raster analysis offered in our tools, the data are automatically resampled to 100 m and mosaiced together for a country extent.
The function is also provided as [**jupyter notebook**](../tools/utility/Fetch_data/Fetch_WSF19.ipynb) you can download and run on your python environment.

(mapping)=
## Mapping in jupyter notebook
Mapping geospatial data doesn't strictly require GIS programs. Some decent results can be achieved with Folium and similar libraries.
An example is provided as [**jupyter notebook**](../tools/utility/mapping.ipynb) you can download and run on your python environment.

(external-tools)=
# External tools
Additional tools to help collect, view and process risk data.

```{table}
:name: external_tools

| **Name** | **License** | **Description** | **Purpose** |
|---:|---:|---:|---:|
| [QGIS](https://qgis.org) | GNU | GIS software | Open, plot, manipulate geodata |
```
The most commonly used software for geodata visualization and processing is QGIS, which comes with a rich [documentation](https://docs.qgis.org).

```{figure} images/qgis.jpg
---
align: center
---
Example of QGIS project
```