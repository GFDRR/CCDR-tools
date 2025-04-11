# Additional tools and data sources

Additional sources of risk data (hazard, exposure, disaster losses) and processing workflows.

```{table}
:name: external_links

| **Name** | **License** | **Description** | **Purpose** |
|---:|---:|---:|---:|
| [Planetary Computer](https://planetarycomputer.microsoft.com/) | GNU | Global environmental geodata as STAC catalog | Geodata catalog |
| [GEE data catalog](https://developers.google.com/earth-engine/datasets/catalog) | GNU | Global environmental geodata as API catalog | Geodata catalog |
| [Awesome GEE community catalog](https://gee-community-catalog.org) | GNU | Community-sourced geodata as Earth Engine assets | Geodata catalog |
| [CLIMAAX](https://handbook.climaax.eu) | GNU | Methods and workflows as notebooks for Climate Risk Assessments (CRA) based on ECMWF data | Handbook |
```

The **Planetary Computer** combines a multi-petabyte catalog of global environmental data with intuitive APIs, a flexible scientific environment that allows users to answer global questions about that data, and applications that put those answers in the hands of researchers and stakeholders.

```{note}
There is a nice [**QGIS plugin**](https://stac-utils.github.io/qgis-stac-plugin/) that allows you to directly get data in the software.

```{figure} images/stac.png
---
align: center
---
Planetary Computer as STAC catalogue accessed via [QGIS](external-tools) using STAC plugin.

```

The **Google Earth Engine (GEE) catalog** includes a variety of standard Earth science raster datasets. You can import these datasets into your script environment with a single click. You can also upload your own raster data or vector data for private use or sharing in your scripts.
<br><br>
The **Awesome GEE community catalog** consists of community sourced geospatial datasets made available for use by the larger Google Earth Engine community and shared publicly as Earth Engine assets. The project was started with the idea that a lot of research datasets are often unavailable for direct use and require preprocessing before use. This catalog lives and serves alongside the Google Earth Engine data catalog and also houses datasets that are often requested by the community and under a variety of open license.
<br><br>
The **CLIMAAX handbook** builds upon existing risk assessment frameworks, methods and tools, and promotes the use of datasets and service platforms for local and regional scale deployment. It develops a robust and coordinated framework of consistent, harmonised and comparable risk assessments via python notebooks.