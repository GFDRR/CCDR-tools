# Results presentation
This section is still work in progress.

[//]: # (Comment)

# Maps
The best way to depict spatial variability is through maps. For baseline risk mapping, there is no simple automation; [QGIS](external-tools) is used to import the data and print into maps.
- The geopackage and tiff data produced by the tool can be simply dragged within QGIS main window to import them in the Table of Content (Toc).
- You can add a basemap for reference. The best way is using the [Quick Map Service](https://opengislab.com/blog/2018/4/15/add-basemaps-in-qgis-30) plugin.
- A proper [symbology](https://docs.qgis.org/3.34/en/docs/training_manual/basic_map/symbology.html) should be applied to each layer.
- The [print layout](https://docs.qgis.org/3.34/en/docs/user_manual/print_composer/index.html) window is used to build the map to export as a picture, adding legends, scale bar, etc.

# Figures

- Charts allow to give a quick snapshots of key output, e.g. the most risk-prone units in a country.
    ```{figure} images/EAI_chart.png
    ---
    align: center
    width: 50%
    ---
    Example of chart depicting absolute and relative EAI.
    ```
- Charts are also better than maps to display the difference between baseline and future risk.
    ```{figure} images/EAI_change_chart.png
    ---
    align: center
    width: 50%
    ---
    Example of chart depicting absolute EAI for historical baseline and future projection scenario.
    ```
# Dashboard

An open dashboard based on R-shiny has been developed in order to quickly disseminate results of risk screening and assessment.
See the [**DEMO for Nigeria**](https://szhaider.shinyapps.io/NigeriaDisasterRisks).

```{figure} images/dashboard.jpg
---
align: center
---
Example of R-shiny dashboard for dissemination of risk screening results.
```