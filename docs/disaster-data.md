# Disaster records

When developing a risk model, hazard models and risk results should be always compared and validated against observed (empirical) disaster events.
The table below lists some of the online portals that provide global disaster data. 
```{table}
:name: foundational_datasets

| **Name** | **Developer** | **Hazard covered** | **Scale** | **Data format** |
|---:|---:|---:|---:|---:|
| [EM-DAT](https://public.emdat.be) | CRED | Multihazard | Subnational level; list of locations | Table |
| [Desinventar](https://www.desinventar.net/DesInventar) | UNDRR | Multihazard | Subnational level | Table, figures |
| [UNOSAT](https://unosat.org/products) | UNITAR | Multihazard | 10 m | Table, map data, reports |                
| [ReliefWeb](https://reliefweb.int) | OCHA | Multihazard | National to local | Reports, figures |  
```
The most commonly used for multi-hazard disasters is EM-DAT, followed by Desinventar. The DesInventar database effectively has no inclusion criteria and therefore, almost all the disaster events are registered into this database. Whereas, the EMDAT database, have a relatively stringent inclusion criterion which may prohibit many small-scale disaster events to be included into the database [(read more)](https://link.springer.com/article/10.1007/s41885-019-00052-0).

```{figure} images/emdat_count.png
---
width: 600
align: center
---
Example of subnational disaster counting in Cambodia for the last 40 years from EMDAT data elaboration.
```

```{figure} images/emdat_maps.jpg
---
width: 600
align: center
---
Example of subnational disaster frequency mapping in Cambodia for the last 40 years from EMDAT data elaboration.
```

The UNOSAT page is the best global source of remote-sourced hazard data, in particular for flood hazard: recent flood events are often available for download as geospatial data representing the water extent as obtained from satellite images interpretation, together with a quick exposure analysis of affected population.

```{figure} images/unosat.jpg
---
width: 600
align: center
---
Example of remote mapping of a recent flood event occurring in Ethiopia and Somalia ([Source](https://unosat.org/products/3563)).
```

For a more detailed analysis, local disaster data should be considered.
When investigating individual disaster events, one of the best sources is [**ReliefWeb**](https://reliefweb.int), a humanitarian information portal by the UN Office for the Coordination of Humanitarian Affairs (OCHA) hosting more than 720,000 humanitarian situation reports, press releases, evaluations, guidelines, assessments, maps and infographics.