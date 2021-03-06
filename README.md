# CCDR ANALYTICAL NOTEBOOKS
A collection of Python notebooks to perform country-level climate and disaster risk analysis based on global data.

## [Top-down](https://github.com/GFDRR/CCDR-tools/tree/main/Top-down)
**Multi-hazard risk screening based on global/regional datasets for selected country and administrative level**

  - **[Flood](https://github.com/GFDRR/CCDR-tools/blob/main/Top-down/notebooks/Flood.ipynb)** - uses flood model (water depth for multiple return periods) to calculate:
	1) Expected Annual Impact (EAI) over population (mortality) and built-up (physical damage) according to vulnerability functions;
	2) distribution of any exposed category (population, built-up or agricultural land) across hazard thresholds.

  - **[Heat stress](https://github.com/GFDRR/CCDR-tools/blob/main/Top-down/notebooks/Heat_stress.ipynb)** - uses heat stress index (multiple return periods) to calculate distribution of exposed population across hazard thresholds (3 classes).
 
  - **Drought** - uses drought frequency index (multiple hazard thresholds) to calculate distribution of exposed agricultural land across hazard thresholds.
  
  - **[Landslide](https://github.com/GFDRR/CCDR-tools/blob/main/Top-down/notebooks/Landslide.ipynb)** - uses landslide hazard index (individual layer) to calculate distribution of exposed categories (population, built-up) across hazard thresholds (3 classes).
  
  - **[Tropical cyclones](https://github.com/GFDRR/CCDR-tools/blob/main/Top-down/notebooks/Tropical_cyclones.ipynb)** - uses wind hazard model (gust speed for 3 return periods) to calculate impact over built-up according to damage function.
  
  - **[Air Pollution](https://github.com/GFDRR/CCDR-tools/blob/main/Top-down/notebooks/AirPollution.ipynb)** - uses PM2.5 hazard map (individual layer) to calculate health impact on population according to mortality function.

## Bottom-up
**Country-specific, detailed risk evaluation based on mix of regional and local data**

- **[Pakistan](https://github.com/mahamfkhan/Pakistan-CCDR)** - Welfare Implications of Climate Change. Fine-tuned analysis of local vulnerability factors and risk channels. Integration of local data and a strong focus on resilience, adaptive capacity and adaptation measures.


## Visualisation
- [SAR-CCDR visualisation](https://github.com/klee016/SAR-CCDR-visualizations) (charts and diagrams)
