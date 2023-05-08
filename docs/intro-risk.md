# Impact and risk

In this framework, Risk (**R**) is calculated as a function of: the hazard occurrence probability and intensity (i.e., physical magnitude) in a particular location (**H**, for Hazard); the people and physical assets (infrastructure, buildings, crops, etc.) situated in that location and therefore exposed to the hazard (**E**, for Exposure); and the conditions determined by physical, social, and economic factors which increase the susceptibility of an exposed individual, community, asset or system to the impacts of hazards (**V**, for Vulnerability).

<span style="font-size: 120%;"><p align="center" size=+2><b>Risk = Hazard x Exposure x Vulnerability</b></p></span>

```{seealso}
**Disaster risk is expressed as the likelihood of loss of life, injury or destruction and damage from a disaster in a given period of time (UNDRR 2019).**

Measures of exposure can include the number of people or types of assets in an area. These can be combined with the specific vulnerability and capacity of the exposed elements to any particular hazard to estimate the quantitative risks associated with that hazard in the area of interest.

- [**UNDRR Risk overview**](https://www.preventionweb.net/understanding-disaster-risk/component-risk/disaster-risk)
```

From these definitions, we understand that the concept of `risk` is inherently tied to the concept of `probability`, expressed in terms of frequency (also occurrence rate). In other words:

<span style="font-size: 120%;"><p align="center" size=+2><b>Risk = Probability x Impact</b></p></span>

```{figure} images/risk_impact_rate.png
---
align: center
---
Risk as impact - probability combination.
```

## Deterministic impact and probabilistic risk
While historical losses can explain the past, they do not necessarily provide a good guide to the future; *most disasters that could happen have not happened yet*. Probabilistic risk assessment simulates those future disasters which, based on scientific evidence, are likely to occur. As a result, these risk assessments resolve the problem posed by the limits of historical data. Probabilistic models therefore *complement* historical records by reproducing the physics and/or the statistics/statistical distribution of the phenomena and recreating the intensity of a large number of synthetic events.

```{note}
In the context of disaster risk, probability refers to the frequency of occurrence or the `return period` of impacts associated with hazardous events.
```

**Probabilistic risk** is the chance of something adverse (impact) occurring. This method assesses the likelihood of an event(s) and it contains the idea of uncertainty because it incorporates the variability between frequent, low impact events and rare, high impact events.

In contrast, a **deterministic risk** model typically models one scenario representing a real event or an individual, finite risk scenario (e.g. mean, median, worst case), but cannot properly represent the full range of variability around it.
 
When probabilistic hazard scenarios (multiple layers by Return Period) are available to calculate impacts in relation to occurrence frequency, an estimate of the **Expected Annual Impact (EAI)** over exposed categories can be calculated.

## Annual risk baseline
*Baseline* refers to the historical period to which the data refer, as opposed to [risk projections](#climate-change-and-disaster-risk).

- The **EAI** is calculated by multiplying the impact from each scenario with its exceedance probability, and then summing up to obtain the mean annual risk considering the whole range of hazard occurrence probabilities. The exceedance frequency curve highlights the relationship between the return period of each hazard and the estimated impact: the area below the curve represents the total annual damage considering all individual scenario probabilities.

- In lack of a proper vulnerability function, the **EAE** is calculated by multiplying the exposure to each hazard scenario with its exceedance probability, and then summing up to obtain the mean annual risk considering the whole range of hazard occurrence probabilities for a range of hazard thresholds. Risk (**EAE**) is then expressed as *annual exposure to hazard over a certain threshold*.

### Lower and Upper bounds
Originally, the calculation of EAI was performed using the customary approach, as exemplified [here](https://storymaps.arcgis.com/stories/7878c89c592e4a78b45f03b4b696ccac) and [here](https://www.researchgate.net/publication/334005888_A_global_multi-hazard_risk_analysis_of_road_and_railway_infrastructure_assets).

Due to requests from regional teams, a refined calculation of the integral for probabilistic EAI and EAE was included:

- **EAI Lower Bound (EAI_LB)**: calculated as the sum of the area of recangles built below the exceedance probability curve
- **EAI Upper Bound (EAI_UB)**: calculated as the sum of the area of recangles built above the exceedance probability curve
- **EAI**: mean between lower and upper bound

```{figure} images/lowerupper.png
---
align: center
---
The integral below the curve is calculated as the mean of lower and upper bound rectangles areas.
```

### Direct and indirect impacts

- FILL IN -

## Supported Hazard and exposure combinations
The following matrix show the combinations of hazard and exposure for which a vulnerability model is provided, and the type of model, allowing to express the risk either in form of impact (damage) or exposure to hazard classes.

```{figure} images/rsk_combo.png
---
align: center
---
Matrix showing hazard-exposure combinations that can be 1) calculated in terms of impact via a vulnerability model, or 2) classified in terms of expsoure to hazard thresholds.
```

## Climate change and disaster risk
Climate change can increase disaster risk in a variety of ways:
- by altering the frequency, intensity and geographic distribution of weather-related hazards, which may lead to new patterns of risk.
- by affecting vulnerability to hazards, and changing exposure patterns.

In other words, disaster risk can be magnified by climate change: it can increase the hazard while at the same time decreasing the resilience of households and communities. Below are some of the main changes expected by the [IPCC Sixth Assessment Report](https://www.ipcc.ch/report/sixth-assessment-report-cycle/).

- **Storms and flooding:** the water cycle will continue to intensify as the planet warms. That includes extreme monsoon rainfall, but also increasing drought, greater melting of mountain glaciers, decreasing snow cover and earlier snowmelt. Annual average precipitation is projected to increase in many areas as the planet warms, particularly in the higher latitudes.

- **Sea level rise:** the population of coastal areas has grown faster than the overall increase in global population; coastal flooding events could threaten assets worth up to 20% of the global GDP by 2100. Low-lying island states could be completely wiped out by sea level rise.

- **Heat stress:** the most direct impact of global warming will be an increase of temperatures, which will aggravate heat stress consequences on human health and agricultural production, in particular in tropical countries with low capacity for adaptation.

- **Droughts:** there will likely be a large reduction in natural land water storage in two-thirds of the world, especially in the Southern Hemisphere. The number of people suffering extreme droughts across the world could double in less than 80 years, which has major implications for the livelihoods of the rural poor, and can also lead to increased migration streams.

- **Tropical cyclones:** even though the attribution of these events to climate change is difficult, a robust increase of the most devastating storms with climate change is expected. Under 2.5°C of global warming, the most devastating storms are projected to occur up to twice as often as today.

See the next chapter for more details.