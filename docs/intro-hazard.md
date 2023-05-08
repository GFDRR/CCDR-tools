# Natural hazards

Natural events (including extreme events and long term phenomena) are only termed hazards when they have the potential to harm people or cause property damage, social and economic disruption. The location of natural hazards primarily depends on natural processes, including the movement of tectonic plates, the influence of weather systems, and the morphology of the terrain (slopes, drainage, vegetation, ...). Anthropic processes such as urbanization, environmental degradation and climate change can also influence the location, occurrence frequency and intensity of natural hazards. These processes are known as risk drivers.

Some of the hazards typically considered in risk screening are:

- **Geophysical hazards**
  - Earthquakes
  - Tsunami
  - Volcanic activities
<br><br>
- **Hydro-meteorological hazards**
  - River and pluvial floods
  - Coastal floods
  - Landslides
  - Tropical cyclones
  - Drought
  - Heat stress
  - Wildfires

Climate change has the potential to affect the frequency and intensity of hydrometeorological hazards (see [**climate outlook**](climate-risk)), while it doesn't significantly affect geophysical hazards.

```{seealso}
**A hazard is a process or phenomenon that may cause loss of life, injury or other health impacts, property damage, social and economic disruption or environmental degradation. Hazards may be natural, anthropogenic or socionatural in origin (UNDRR 2019).**

- **[UNDRR Hazard overview](https://www.preventionweb.net/understanding-disaster-risk/component-risk/hazard)**

- **[UNDRR Hazard definition & classification review](https://www.undrr.org/publication/hazard-definition-and-classification-review-technical-report)**
```
**Natural Hazard Data** include hazard datasets representing intensity and the models (code) or approaches that are used to produce them.

## Intensity and frequency

**Hazard intensity** is one of the key factors that determine the size of the impact over exposed elements.

```{figure} images/hzd_intensity.jpg
---
align: center
---
```

The modelling of hazard intensity can be either:

- **Deterministic**, in the form of an individual geodata layer measuring the mean, median or maximum intensity of a hazard aggregating historical data and modelling (this is the case for landslide and drought hazard in the current data pool).

- **Probabilistic**, in the form of multiple geodata layers, each representing a range of hazard physical intensities (e.g. water depth [m], wind speed [km/h]) corresponding to a specific occurrence frequency, measured as Return Period (RP), in years (this is the case for river flood, coastal flood and strong winds in the current data pool).


```{seealso}
**Raw hazard data (model output) usually come in the form of one or more georeferenced layers.**

- **[Geospatial data and GIS](https://centre.humdata.org/learning-path/an-introduction-to-geospatial-data/geospatial-data-geographic-information-systems/)**
```
See the picture below as example: the landslide hazard (first map) is represented by one aggregated mean index value; while the flood hazard is shows as a series of events (scenarios) of increasing magnitude and decreasing probability.

```{figure} images/hzd_models.jpg
---
width: 100%
align: center
---
```

A probabilistic hazard representation is required in order to produce [probabilistic risk](intro-risk#determimistic-and-probabilistic-risk) mapping.

```{note}
Note that a return period of 1,000 years, while very unlikely, can occur anyday! Therefore it is important to consider all range of probabilities when assessing risk.<br><p align=center><b>RP 1,000 = change of occurring once every 1,000 years = 1/1,000 annual occurrence probability (0.001 or 0.1% any given year).</b></p>
```

Hazard models carry **limitations related to their applicability**. Their quality depend on scale, resolution, model quality, training period and related input data quality.
As a rule of thumb, their fitness for application in the context of a risk screening or assessment exercise depends on the scale of the risk analysis, i.e. locally-sourced models are expeceted to be best fitted for local scale assessment (e.g. city level), while global models are best suited for national or sub-national estimates.

In the context of developing countries, however, a global model is often the only available source for a location. In those cases, the application of the global model must be taken with caution and correctly interpreted acknowledging the limitations. See [**uncertainty**](validation#uncertainty).

```{caution}
When it comes to natural hazards and risk, **misinformation can be worse than no information at all**.
```
