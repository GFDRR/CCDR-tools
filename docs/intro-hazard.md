# Natural hazards

Natural phenomena, whether extreme events or long-term processes, become hazards only when they pose potential harm to people, property, or socioeconomic systems. The occurrence of these natural hazards is primarily determined by physical factors, such as weather system dynamics, tectonic plate movements and terrain characteristics (e.g., slopes, drainage, vegetation).
Anthropogenic factors, such as urbanization, environmental degradation and climate change, are known as *risk drivers* as they can influence the location, frequency, and intensity of natural hazards.
The inherently geographical nature of both natural hazards and exposure necessessarily requires a geospatial approach to properly understandi and interpret the risk.
In other words, the spatial dimension is crucial for effective risk assessment and management strategies.

```{seealso}
**A hazard is a process or phenomenon that may cause loss of life, injury or other health impacts, property damage, social and economic disruption or environmental degradation. Hazards may be natural, anthropogenic or socionatural in origin (UNDRR 2019).**

- **[UNDRR Hazard overview](https://www.preventionweb.net/understanding-disaster-risk/component-risk/hazard)**

- **[UNDRR Hazard definition & classification review](https://www.undrr.org/publication/hazard-definition-and-classification-review-technical-report)**
```

- **Geophysical Hazards** typically include Earthquakes, Tsunami and Volcanic activities.
- **Hydro-meteorological** Hazards include Floods, Landslides, Tropical cyclones, Drought, Heat stress and Wildfires.

While it doesn't significantly affect geophysical hazards, **climate change** has the potential to affect the frequency and intensity of hydrometeorological hazards (see [**climate outlook**](climate-risk)).

```{figure} images/hzd_spectrum.png
---
align: center
---
```

## Intensity and frequency

**Hazard intensity** is one of the key factors that determine the size of the impact over exposed elements. Hazard data usually come in the form of one or more georeferenced layers representing their intensity in relation to location. The modelling of hazard intensity (sometimes called magnitude) can be either:

- **Deterministic**, in the form of an individual geodata layer measuring the mean, median or maximum intensity of a hazard aggregating historical data and modelling.
- **Probabilistic**, in the form of multiple geodata layers, each representing a range of hazard physical intensities corresponding to a specific occurrence frequency, measured as Return Period (RP), in years.

See the picture below as example: the landslide hazard (_left_) is represented by one aggregated mean index value; while the flood hazard is shows as a series of events (scenarios) of increasing magnitude and decreasing probability. A probabilistic hazard representation is required in order to produce [probabilistic risk](probabilistic-risk) mapping.

```{figure} images/hzd_models.jpg
---
width: 100%
align: center
---
```

```{note}
Note that a return period of 1,000 years, while very unlikely, can occur anyday! Therefore it is important to consider all range of probabilities when assessing risk.<br><p align=center><b>RP 1,000 = chance of occurring once every 1,000 years<br>= 1/1,000 annual occurrence probability (0.001 or 0.1% any given year).</b></p>Read more:
- [Understanding flood risk](https://thefloodhub.co.uk/blog/understanding-flood-risk)
- [Communicating the chance of a flood: The use and abuse of probability, frequency and return period](https://www.researchgate.net/publication/328368702_Communicating_the_chance_of_a_flood_The_use_and_abuse_of_probability_frequency_and_return_period)
```

Hazard models carry **limitations related to their applicability**. Their quality depend on scale, resolution, model quality, training period and related input data quality.
As a rule of thumb, their fitness for application in the context of a risk screening or assessment exercise depends on the scale of the risk analysis, i.e. locally-sourced models are expeceted to be best fitted for local scale assessment (e.g. city level), while global models are best suited for national or sub-national estimates.

In the context of developing countries, however, a global model is often the only available source for a location. In those cases, the application of the global model must be taken with caution and correctly interpreted acknowledging the limitations. See [**uncertainty**](uncertainty).

```{caution}
When it comes to natural hazards and risk,<center>**MISINFORMATION CAN BE WORSE THAN NO INFORMATION AT ALL!**</center>
```

```{seealso}
An introduction to **[Geospatial data and GIS](https://centre.humdata.org/learning-path/an-introduction-to-geospatial-data/geospatial-data-geographic-information-systems/)**.
```
