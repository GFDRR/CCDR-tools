# Additional resources

## Additional data sources
Additional sources of risk data (hazard, exposure, disaster losses) and processing workflows.

```{table}
:name: external_links

| **Name** | **License** | **Description** | **Purpose** |
|---:|---:|---:|---:|
| [Planetary Computer](https://planetarycomputer.microsoft.com/) | GNU | Global environmental geodata as STAC catalog | Geodata catalog |
| [GEE data catalog](https://developers.google.com/earth-engine/datasets/catalog) | GNU | Global environmental geodata as API catalog | Geodata catalog |
| [Awesome GEE community catalog](https://gee-community-catalog.org) | GNU | Community-sourced geodata as Earth Engine assets | Geodata catalog |
| [UNEP CDRI](https://handbook.climaax.eu) | GNU | Open-access global hazard maps and risk estimates | Geodata catalog |
| [DECAT Space2Stats](https://worldbank.github.io/DECAT_Space2Stats) | GNU | Global boundaries at the ADM2 level | Geodata catalog |
| [Geoboundaries](https://www.geoboundaries.org) | GNU | Global boundaries for different ADM levels | Geodata catalog |
| [CLIMAAX](https://handbook.climaax.eu) | GNU | Methods and workflows as notebooks for Climate Risk Assessments (CRA) based on ECMWF data | Handbook |
| [Critical Infrastructures Risk](https://vu-ivm.github.io/GlobalInfraRisk) | GNU | Methods and workflows as notebooks for assessing impacts over critical infrastructures | Handbook |
| [PYTHIA](https://foundations.projectpythia.org) | GNU | Methods and workflows as notebooks for geo-mapping | Handbook |
```

The [**Planetary Computer**](https://planetarycomputer.microsoft.com/) combines a multi-petabyte STAC catalog of global environmental data with intuitive APIs, a flexible scientific environment that allows users to answer global questions about that data, and applications that put those answers in the hands of researchers and stakeholders.

```{note}
There is a nice [**QGIS plugin**](https://stac-utils.github.io/qgis-stac-plugin/) that allows you to directly get data in the software.

```{figure} images/stac.png
---
align: center
---
Planetary Computer as STAC catalogue accessed via [QGIS](external-tools) using STAC plugin.

```

The [**Google Earth Engine (GEE) catalog**](https://developers.google.com/earth-engine/datasets/catalog) includes a variety of standard Earth science raster datasets. You can import these datasets into your script environment with a single click. You can also upload your own raster data or vector data for private use or sharing in your scripts.
<br><br>

The [**Awesome GEE community catalog**](https://gee-community-catalog.org) consists of community sourced geospatial datasets made available for use by the larger Google Earth Engine community and shared publicly as Earth Engine assets. The project was started with the idea that a lot of research datasets are often unavailable for direct use and require preprocessing before use. This catalog lives and serves alongside the Google Earth Engine data catalog and also houses datasets that are often requested by the community and under a variety of open license.
<br><br>

The [**Global Infrastructure Risk Model and Resilience Index (GIRI) Map Viewer**](https://giri.unepgrid.ch/map) is an interactive platform developed by UNEP in collaboration with the Coalition for Disaster Resilient Infrastructure (CDRI). It provides a comprehensive, probabilistic assessment of disaster risks to infrastructure assets worldwide, encompassing both current conditions and future climate scenarios for major natural hazards—including earthquakes, tsunamis, tropical cyclones, floods, landslides, and droughts.
The Map Viewer features over 100 hazard and risk layers, allowing users to explore detailed scenarios and customize analyses. It serves as a vital tool for policymakers, planners, and researchers aiming to develop informed, risk-aware infrastructure policies and investments.
<br><br>

The [**DECAT Space2Stats program**](https://worldbank.github.io/DECAT_Space2Stats) program is designed to provide academics, statisticians, and data scientists with easier access to regularly requested geospatial aggregate data: Official World Bank boundaries at admin level 2 and a global database of hexagons (~36km2).

The [**Geoboundaries global database**](https://www.geoboundaries.org) is an open-access repository offering detailed, research-ready political administrative boundaries for every country in the world, up to five levels of administrative hierarchy.

## External analytical tools

The [**CLIMAAX handbook**](https://handbook.climaax.eu) builds upon existing risk assessment frameworks, methods and tools, and promotes the use of datasets and service platforms for local and regional scale deployment. It develops a robust and coordinated framework of consistent, harmonised and comparable risk assessments via python notebooks.
<br><br>

The [**Critical Infrastructure handbook**](https://vu-ivm.github.io/GlobalInfraRisk) provides an open-source framework for assessing the risk of critical infrastructure worldwide. By leveraging publicly available datasets and analytical tools, it enables users to evaluate infrastructure exposure, vulnerability, and potential damage due to natural hazards.
<br><br>

The [**Pythia Foundations**](https://foundations.projectpythia.org) is an open-access educational resource developed by the Project Pythia community. It offers comprehensive tutorials and interactive content designed to teach foundational skills in scientific computing with Python, particularly tailored for the geosciences. In particular, it provides in-depth tutorials on key Python libraries like NumPy, Pandas, Matplotlib, Xarray, and Cartopy, which are vital for data analysis and visualization in scientific research.