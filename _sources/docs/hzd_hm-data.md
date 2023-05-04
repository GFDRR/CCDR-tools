# Hydro-Meteorological hazards

Process or phenomenon of atmospheric, hydrological or oceanographic nature that may cause loss of life, injury or other health impacts, property damage, loss of livelihoods and services, social and economic disruption, or environmental damage [(UNISDR)](https://link.springer.com/referenceworkentry/10.1007/978-1-4020-4399-4_179#ref-CR8537).

## River floods
Flood hazard is commonly described in terms of flood frequency (multiple scenarios) and severity, which is measured in terms of water extent and related depth modelled over Digital Elevation Model (DEM). Inland flood events can be split into 2 categories:
- **Fluvial (or river) floods** occur when intense precipitation or snow melt collects in a catchment, causing river(s) to exceed capacity, triggering the overflow, or breaching of barriers and causing the submersion of land, especially along the floodplains.
- **Pluvial (or surface water) floods** are a consequence of heavy rainfall, but unrelated to the presence of water bodies. Fast accumulation of rainfall is due to reduced soil absorbing capacity or due to the saturation of the drainage infrastructures; meaning that the same event intensity can trigger very different risk outcomes depending on those parameters. For this reason, static hazard maps based on rainfall and DEM alone should be used with extreme caution.

```{table}
:name: FL_data
**Name** | [Fathom flood hazard maps](https://www.fathom.global/) | [Aqueduct flood hazard maps](https://www.wri.org/data/aqueduct-floods-hazard-maps)
--: | :--: | :--:
**Developer** | Fathom | WRI
**Hazard process** | Fluvial flood, Pluvial flood | Fluvial flood
**Resolution** | 90 m | 900 m
**Analysis type** | Probabilistic | Probabilistic
**Frequency type** | Return Period (11 RPs) | Return Period (10 RPs)
**Time reference** | Baseline (1989-2018) | Baseline (1960-1999); Projections  – CMIP5 (2030-2050-2080)
**Intensity metric** | Water depth [m] | Water depth [m]
**License** | Commercial | Open data
**Other** | Includes defended/undefended option |  
**Notes** | Standard for WB analysis | The only open flood dataset addressing future hazard scenarios
```

- Despite missing projections, **Fathom** modelling has consistently proven to be the preferred option due to its higher quality (better resolution, updated data and a more advanced modelling approach). There are, however, important details and limitations to consider for the correct use and interpretation of the model. The undefended model (FU) is typically the preferred product to use in assessments, since the defended model (FD) does not account for physical presence of defense measures, rather proxies the defense standard by using GDP as proxy (FLOPROS database).

```{seealso}
The Fathom v2 global dataset can be requested for use in World Bank projects by filling the [**request form**](https://forms.office.com/r/RzNaVV3mft).
```

- **WRI** hazard maps are the preferred choice only in cases when 1) data needs to be open/public; 2) explicit climate scenarios are required, however the scientific quality and granularity of this dataset is far from the one offered by Fathom – and far from optimal, in general (low resolution, old baseline, simplified modelling).

[insert map comparison]

It is important to note that pluvial (flash) flood events are extremely hard to model properly on the base of global static hazard maps alone. This is especially true for densely-populated urban areas, where the hazardous water cumulation is often the results of undersized or undermaintained discharge infrastructures. Because of this, while Fathom does offer pluvial hazard maps, their application for pluvial risk assessment is questionable as it cannot account for these key drivers.

A complementary perspective on flood risk is offered by the [Global Surface Water layer](https://planetarycomputer.microsoft.com/dataset/jrc-gsw) produced by JRC using remote sensing data (Landsat 5, 7, 8) over the period1984-2020. It provides information on all the locations ever detected as max water level, water occurrence, occurrence change, recurrence, seasonality, and seasonality change. However, this layer does not seem to properly account for extreme flood events, I.e. recorded flood events for the period 1984-2020 most often exceed the extent of this layer. Hence it can be used to identify permanent and semi-permanent water bodies, but not to identify the baseline flood extent from past events.

```{figure} images/GSWL.jpg
---
align: center
---
Global Surface Water Layer
```

## Coastal floods (storm surge)
Coastal floods occur when the level in a water body (sea, estuary) rises to engulf otherwise dry land. This happens mainly due to storm surges, triggered by tropical cyclones and/or strong winds pushing surface water inland. Like for inland floods, hazard intensity is measured using the water extent and associated depth.

```{table}
:name: CF_data
| **Name** | [Aqueduct flood hazard maps](https://www.wri.org/data/aqueduct-floods-hazard-maps) | [Global Flood map](https://planetarycomputer.microsoft.com/dataset/deltares-floods) |
|---:|:---:|:---:|
| **Developer** | WRI-Deltares | Deltares |
| **Hazard process** | Coastal flood | Coastal flood, SLR |
| **Resolution** | 1 km | 90 m, 1 km, 5 km |
| **Analysis type** | Probabilistic | |
| **Frequency type** | Return Period (10 RPs) | Return Period (6 RPs) |
| **Time reference** | Baseline (1960–1999);<br>Projections – CMIP5 (2030-2050-2080) | Baseline (2018);<br>Projections – SLR (2050) |
| **Intensity metric** | Water depth [m] | Water depth [m] |
| **License** | Open data | Access requested |
| **Notes** | Includes effect of local subsidence (2 datasets) and flood attenuation. Modelled future scenarios. | Essentially an evolution of the WRI |
```

The current availability of global dataset is poor, with WRI products (recently updated by Deltares) representing the best option in terms of resolution and time coverage (baseline + scenarios), and water routing, including inundation attenuation to generate more realistic flood extent. The latest version has a much better resolution of 90 m based on MeritDEM or NASADEM, overcoming WRI limitations for local-scale assessment. Note that the Fathom is working to include coastal floods and climate scenarios in the next version (3) of the dataset (coming sometime in 2023/24), which will likely become the best option for risk assessment in the next future.

Additional datasets that have been previously used in WB coastal flood analytics are:

```{table}
:name: CF_data_more
| **Name** | [Coastal flood hazard maps](https://www.geonode-gfdrrlab.org/search/?hazard_type=coastal_flood&limit=5&offset=5&type__in=raster&title__icontains=muis) | [Coastal risk screening](https://coastal.climatecentral.org) |
|---:|:---:|:---:|
| **Developer** | Muis et al. (2016, 2020) | Climate Central |
| **Hazard process** | Coastal flood | Mean sea level |
| **Resolution** | 1 km | |
| **Analysis type** | Probabilistic | |
| **Frequency type** | Return Period (10 RPs) | One layer per period |
| **Time reference** | Baseline (1979–2014) | Baseline; Projections |
| **Intensity metric** | Water depth [m] | Water extent |
| **License** | Open data | Licensed |
| **Notes** | The update of Muis 2020 has been considered; however, the available data does include easily applicable land inundation, only extreme sea levels. | Does use simple bathtub distribution without flood attenuation – does not simulate extreme sea events. |
```

Both these models seem to be affrom a simplified bathtub modelling approach, projecting unrealistic flood extent already under baseline climate conditions.

As shown in figure below, considering the minimum baseline values (least impact criteria), the flood extent drawn by the Climate Central layer is similar to the baseline RP100 from Muis, in the middle - both generously overestimating water spreading inland even under less extreme scenarios [*the locaiton of comparison is chosen as both the Netherlands and N Italy are low-lying areas, which are typically the most difficult to model*].
In comparison, the WRI is far from perfection (it is also a bathtub model), but it seems to apply a more realistic max flood extent, which ultimately makes it more realistic for application.

```{figure} images/CF_data.jpg
---
align: center
---
Quick comparison of coastal flood layers over Northern Europe under baseline conditions, RP 100 years.
```
### Sea level rise

## Landslides
Landslides (mass movements) are affected by geological features (rock type and structure) and geomorphological setting (slope gradient). Landslides can be split into two categories depending on their trigger:
- **Dry mass movement** (rockfalls, debris flows) is driven by gravity and can be triggered by seismic events, but they can also be a consequence of soil erosion and environmental degradation. 
- **Wet mass movement** can be triggered by heavy precipitation and flooding and are strongly affected by geological features (e.g. soil type and structure) and geomorphological settings (e.g., slope gradient). They do not typically include avalanches.

```{table}
:name: LS_data
| **Name** | [Global landslide hazard layer](https://datacatalog.worldbank.org/search/dataset/0037584/Global-landslide-hazard-map) | [Global landslide susceptibility (LHASA)](https://gpm.nasa.gov/landslides/projects.html) |
|---:|:---:|:---:|
| **Developer** | ARUP | NASA |
| **Hazard process** | Dry (seismic) mass movement Wet (rainfall) mass movement | Wet (rainfall) mass movement |
| **Resolution** | 1 km | 1 km |
| **Analysis type** | Deterministic | Deterministic |
| **Frequency type** | none | none |
| **Time reference** | Baseline (rainfall trigger) (1980-2018) | |
| **Intensity metric** | Hazard index [-] | Susceptibility index [-] |
| **License** | Open | |
| **Notes** | Based on NASA landslide susceptibility layer. Median and Mean layers provided. | Although not a hazard layer, it can be accounted for in addition to the ARUP layer. |
```

Landslide hazard description can rely on either the NASA Landslide Hazard Susceptibility map (LHASA) or the derived ARUP layer funded by GFDRR in 2019. This dataset considers empirical events from the COOLR database and model both the earthquake and rainfall triggers over the existing LHASA map. The metric of choice is frequency of occurrence of a significant landslide per km2, which is however provided as synthetic index (not directly translatable as time occurrence probability).

```{figure} images/LS_data.jpg
---
align: center
---
Example from the ARUP landslide hazard layer (rainfall trigger, median): Pakistan. The continuos index is displayed into 3 discrete classes (Low, Medium, High).
```

## Tropical cyclones
Tropical cyclones (including hurricanes, typhoons) are events that can trigger different hazard processes at once such as strong winds, intense rainfall, extreme waves, and storm surges. In this category, we consider only the wind component of cyclone hazard, while other components (floods, storm surge) are typically considered separately.

```{table}
:name: SW_data
| **Name** | [GAR15-IBTrACS](https://www.geonode-gfdrrlab.org/search/?hazard_type=strong_wind&limit=50&offset=0&title__icontains=CY-GLOBAL) | [IBTrACSv4](https://www.ncei.noaa.gov/products/international-best-track-archive?name=ib-v4-access) | [STORMv3](https://data.4tu.nl/articles/dataset/STORM_tropical_cyclone_wind_speed_return_periods/12705164/3) |
|---:|:---:|:---:|:---:|
| **Developer** | NOAA | NOAA | IVM |
| **Hazard process** | Strong winds | Strong winds | Strong winds |
| **Resolution** | 30 km | 10 km | 10 km |
| **Analysis type** | Probabilistic | Empirical | Empirical, Probabilistic |
| **Frequency type** | Return Period (5 RPs) | | Return periods (10 10,000 years) |
| **Time reference** | Baseline (1989-2007) | Baseline (1980-2022) | Baseline (1984-2022);<br>Projections (2015-2050; SSP5/8.5) |
| **Intensity metric** | Wind gust speed [5-sec m/s] | Many variables | Many variables |
| **License** | Open data | Open data | Open data |
```

A newer version ([IBTrACSv4](https://www.ncei.noaa.gov/products/international-best-track-archive?name=ib-v4-access)) has been released in 2018 and could be leveraged to generate an updated wind-hazard layer, with better resolution and possibly the inclusion of orography effect. There are several attributes tied to each event; the map in figure below shows the USA_WIND variable (Maximum sustained wind speed in knots: 0 - 300 kts) as general intensity measure.

The STORM database has recently released their new version ([STORMv3](https://data.4tu.nl/articles/dataset/STORM_tropical_cyclone_wind_speed_return_periods/12705164/3)), which includes synthetic global maps of 1) maximum wind speeds for a fixed set of return periods; and 2) return periods for a fixed set of maximum wind speeds, at 10 km resolution over all ocean basins. In addition, it contains the same set for events occurring within 100 km from a selection of 18 coastal cities and another for events occurring within 100 km from the capital city of an island.
The STORM dataset comes with [projections](https://data.4tu.nl/articles/dataset/STORM_Climate_Change_synthetic_tropical_cyclone_tracks/14237678/1) as described in [Bloemendaal, et al., 2022](https://www.science.org/doi/10.1126/sciadv.abm8438): those are generated by extracting the climate change signal from each of the four general circulation models listed below, and adding this signal to the historical data from IBTrACS. This new dataset is then used as input for STORM, and resembles future-climate (2015-2050; RCP8.5/SSP5) conditions. Both [synthetic tracks](https://data.4tu.nl/articles/dataset/STORM_Climate_Change_synthetic_tropical_cyclone_tracks/14237678/1) and [wind speed maps](https://data.4tu.nl/articles/dataset/STORM_climate_change_tropical_cyclone_wind_speed_return_periods/14510817) are available.
These data can be used to calculate tropical cyclone risk in all (coastal) regions prone to tropical cyclones.

```{figure} images/SW_data.jpg
---
align: center
---
Top: GAR 2015 cyclone max wind speed; Mid: IBTrACS v4 cyclone tracks; Bottom: STORMv3 synthetic cyclone tracks into max wind speed, RP 100 years.
```

## Drought & Water scarcity

The [**Agricultural Stress Index**](https://www.fao.org/giews/earthobservation/access.jsp) by **FAO** depicts the frequency of severe drought in areas where: i) 30 percent of the cropped land; or ii) 50 percent of the cropped land has been affected. The historical frequency of severe droughts (as defined by ASI) is based on the entire the times series (1984-2021). Data are available in 
 
```{figure} images/fao_asi.jpg
---
align: center
---
FAO ASI global dataset showing historical drought frequency for >30% cropland area affected along the period 1984-2021.
```

## Heat stress

Heat discomfort increases when hot temperatures are associated with high humidity [[Coffel et al 2018](https://doi.org/10.1088/1748-9326/aaa00e)]. Heat stress can cause long-term impairment and reduce labour productivity and incomes [[Goodman et [al 2018](https://scholar.harvard.edu/files/joshuagoodman/files/w24639.pdf)].
Extreme heat events lead to heat stress and can increase morbidity and mortality as well as losses of work productivity [Kjellstrom et al 2009, Singh et al 2015].
Not everyone reacts to the heat stresses in the same way, as individual responses are conditional on their medical condition, level of fitness, body weight, age, and economic situation [National Institute for Occupational Safety and Health 2016].

Various definitions regarding magnitude and duration thresholds and heat metrics exist. There are several heat indices involving both temperature and relative humidity, here are listed the most common ones.

Name | [Global extreme temperatures (WBGT)](https://www.geonode-gfdrrlab.org/layers/hazard:intensity_returnperiod5y/metadata_detail) | [Universal Thermal Climate Index (UTCI)](https://climate.copernicus.eu/ESOTC/2019/heat-and-cold-stress) | [Heat-humidity index](https://cds.climate.copernicus.eu/cdsapp#!/dataset/projections-cordex-domains-single-levels?tab=overview)
--: | :--: | :--: | :--:
Developer | VITO | Copernicus | CORDEX
Hazard process | Extreme heat stress | Heat stress on human health | Extreme heat and humidity
Resolution | 10 km | 30 km | 25 km
Analysis type | Probabilistic | Index | Probabilistic
Frequency type | Return Period (3 RPs) | None |  
Time reference | Baseline (1980-2009) | Baseline (1979-2020) | Baseline (1970-2000); Projections (2040-2070, 2070-2100)
Intensity metric | Wet Bulb Globe Temperature [°C] | UTCI (°C) | Heat Index, Humidex
License | Open data | Open data | Open data
Notes | Accounts for air temperature, humidity, wind speed, radiation, fatigue-heating. Includes intensity-impact classification. | Accounts   for air temperature, humidity, wind speed, radiation. Includes intensity-impact classification. |  

- **Wet-Bulb Globe Temperature** (WBGT °C): the WBGT combines temperature and humidity, both critical components in determining heat stress. A probabilistic dataset (3 return periods: 5, 20 and 100 years) based on 1980-2009 data has been developed for the GFDRR by VITO and has since been used to measure heat stress in risk screenings and assessment. This layer is generally sufficient for country-level hazard screening, but it has several limitations for any hazard and risk assessment. Although downscaled to consider gepmorphology and orography, the low grid resolution and relatively simple modelling makes it unfit to capture the heat island effect occurring in cities (Urban Heat Island) – nor the cooling effect of water bodies. That makes it unfit for any urban-scale assessment and generally sub-optimal for any sub-national assessment.

```{figure} images/hzd_hs.jpg
---
align: center
---
Comparing recent high-resolution temperature maps showing the heat island effect in Las Vegas, and the presence of the lake; the WBGT map by VITO cannot capture these details.
```

- **Universal Thermal Climate Index** (UTCI °C): the UTCI is defined as the air temperature of a reference outdoor environment that would elicit in the human body the same physiological model’s response (sweat production, shivering, skin wetness, skin blood flow and rectal, mean skin and face temperatures) as the actual environment.
A polynomial approximation based on near-surface air temperature, solar radiation, vapor pressure, and wind speed is used for calculating the universal thermal climate index.


```{seealso}
UTCI data from ERA-5 climate reanalysis has been processed into a probabilistic analysis of extremes from the [Copernicus CDS](https://cds.climate.copernicus.eu/cdsapp#!/dataset/sis-extreme-indices-cmip6?tab=overview). In this dataset, the influence of solar radiation and wind speed is not considered, and the UTCI is calculated from near-surface air temperature and vapor pressure solely, thus representing indoor or under-shade conditions.
A collection of scenarios representing the frequency distribution of heat has been produced in form of multiple layers representing return periods.
The objective is to facilitate the use of these data for heat risk analysis. The scenarios include ten return periods for mean, min and max daily UTCI (C°) for the period 1940-2020. Return Period scenarios: 5, 10, 20, 50, 75, 100, 200, 250, 500 and 1000 years.<br>`NOT RELEASED YET`.
```

The two indices are similar and [correlated](https://www.sciencedirect.com/science/article/pii/S2212094717302037), but while WBGT considers workload and overall effect on human health, UTCI is a more physically-based measure, thus it is easier to put it in relation to the physical measure of surface temperature (°C). It also has the advantage to consider cold stress extremes as well.

```{figure} images/hzd_hs_class.png
---
align: center
width: 60%
---
```
In terms of future projections, both UTCI and WBGT projections have been produced under CMIP6 scenarios and are available via [Copernicus CDS](https://cds.climate.copernicus.eu/cdsapp#!/dataset/sis-extreme-indices-cmip6?tab=overview). The indices are provided for historical and future climate projections (SSP1-2.6, SSP2-4.5, SSP3-7.0, SSP5-8.5) included in the Coupled Model Intercomparison Project Phase 6 (CMIP6) and used in the 6th Assessment Report of the Intergovernmental Panel on Climate Change (IPCC). These have daily resolution and would allow to derive downscaled extreme temperature projections. These projections have not yet been processed into a frequency analysis, but that can be produced using the same approach.

## Wildfires
