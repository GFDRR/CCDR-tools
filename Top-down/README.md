# CCDR ANALYTICAL NOTEBOOKS
## Multi-hazard risk screening based on global/regional datasets

--------------------------------------

## OVERVIEW
This is an open tool for risk screening based on globally-avaialble datasets. 

The ‘top-down’ approach offers analytical notebooks allowing non-experts to perform comprehensive, multi-hazard risk screening using regionally available and comparable datasets. The work under this tier is characterized by: 

 - Global and regional-scale data inputs 
 - User-friendly, and easily interpretable tools and outputs
 - Some degree of customisation, but ensuring transferability and comparability between countries 

Analysis runs over high resolution exposure data (90 m) and is then aggregated at the required administrative level. This approach provides sub-national mapping of natural hazards, exposure and risk,  which can inform policy and targeted interventions. Risk is calculated independently for each individual hazard.

--------------------------------------

## CONTENT

   - **[Procedures](procedures/)** - explains the analytical workflow used by notebooks with examples for different hazards
   - **[Notebooks](notebooks/)** - include jupyter notebooks to perform the spatial analytics for each hazard
   - **[Parallelization](parallelization/)** - include python scripts (beta) to perform the spatial analytics with better efficiency for each hazard
   
--------------------------------------

  - **[Flood](https://github.com/GFDRR/CCDR-tools/blob/main/Top-down/notebooks/Flood.ipynb)** - uses flood model (water depth for multiple return periods) to calculate:
	1) Expected Annual Impact (EAI) over population (mortality) and built-up (physical damage) according to vulnerability functions;
	2) distribution of any exposed category (population, built-up or agricultural land) across hazard thresholds.

  - **[Heat stress](https://github.com/GFDRR/CCDR-tools/blob/main/Top-down/notebooks/Heat_stress.ipynb)** - uses heat stress index (multiple return periods) to calculate distribution of exposed population across hazard thresholds (3 classes).
 
  - **Drought** - uses drought frequency index (multiple hazard thresholds) to calculate distribution of exposed agricultural land across hazard thresholds.
  
  - **[Landslide](https://github.com/GFDRR/CCDR-tools/blob/main/Top-down/notebooks/Landslide.ipynb)** - uses landslide hazard index (individual layer) to calculate distribution of exposed categories (population, built-up) across hazard thresholds (3 classes).
  
  - **[Tropical cyclones](https://github.com/GFDRR/CCDR-tools/blob/main/Top-down/notebooks/Tropical_cyclones.ipynb)** - uses wind hazard model (gust speed for 3 return periods) to calculate impact over built-up according to damage function.
  
  - **[Air Pollution](https://github.com/GFDRR/CCDR-tools/blob/main/Top-down/notebooks/AirPollution.ipynb)** - uses PM2.5 hazard map (individual layer) to calculate health impact on population according to mortality function.

--------------------------------------

## CREDITS

Tools developed in the context of World Bank CCDR analytics
- Concept: [Mattia Amadio](https://www.github.com/matamadio)
- Coding: [Takuya Iwanaga](https://github.com/ConnectedSystems)
- Additional coding: [Arthur H. Essenfelder](https://github.com/artessen)
