# CCDR ANALYTICAL NOTEBOOKS
## Multi-hazard risk screening based on global/regional geodatasets

--------------------------------------

## OVERVIEW
This is an open tool for risk screening based on globally-avaialble datasets. 

The ‘top-down’ approach offers analytical notebooks allowing non-experts to perform comprehensive, multi-hazard risk screening using regionally available and comparable geodata. The work under this tier is characterized by: 

 - Global and regional-scale geodata inputs 
 - User-friendly, and easily interpretable tools and outputs
 - Some degree of customisation, but ensuring transferability and comparability between countries 

Analysis runs over high resolution exposure data (90 m) and is then aggregated at the required administrative level. This approach provides sub-national mapping of natural hazards, exposure and risk,  which can inform policy and targeted interventions. Risk is calculated independently for each individual hazard.

--------------------------------------

## RATIONALE

The applied methodology centers around the concept of Risk. In the field of Disaster Risk Management (DRM), risk (R) is typically calculated as a function of: the hazard occurrence probability and intensity (i.e., physical magnitude) in a particular location (H, for Hazard); the people and physical assets (infrastructure, buildings, crops, etc.) situated in that location and therefore exposed to the hazard (E, for Exposure); and the conditions determined by physical, social, and economic factors which increase the susceptibility of an exposed individual, community, asset or system to the impacts of hazards (V, for Vulnerability).
Following this established approach, the risk originating from hazard affecting exposed categories is defined as: `R = f(H,E,V)`

<div align="center">
<img width=250 src="https://user-images.githubusercontent.com/44863827/198075495-b2235f1e-755d-461a-9c4a-ceca8bd2b79e.png">
</div>

The analysis workflow:
<div align="center"><img width=500 src="https://user-images.githubusercontent.com/44863827/200046500-2418ed39-88dd-4aa6-acf3-fb2963899db8.png"></div>

--------------------------------------

## CONTENT

   - **[Procedures](procedures/)** - explains the analytical workflow used by notebooks with examples for different hazards
   - **[Notebooks](notebooks/)** - include jupyter notebooks to perform the spatial analytics for each hazard
   - **[Parallelization](parallelization/)** - include python scripts (beta) to perform the spatial analytics with better efficiency for each hazard
   
--------------------------------------

## ANALYSES

  - **Flood** [[Procedure](procedures/Analytical_procedure_function.md) - [Notebook](notebooks/Flood.ipynb)] - uses flood model (water depth for multiple return periods) to calculate:
	1) Expected Annual Impact (EAI) over population (mortality) and built-up (physical damage) according to vulnerability functions;
	2) distribution of any exposed category (population, built-up or agricultural land) across hazard thresholds.

  - **Heat stress** [[Procedure](procedures/Analytical_procedure_classes.md) - [Notebook](notebooks/Heat_stress.ipynb)] - uses heat stress index (multiple return periods) to calculate distribution of exposed population across hazard thresholds (3 classes).
 
  - **Drought** - uses drought frequency index (multiple hazard thresholds) to calculate distribution of exposed agricultural land across hazard thresholds.
  
  - **Landslide** [[Procedure](procedures/Analytical_procedure_classes.md) - [Notebook](notebooks/Landslide.ipynb)] - uses landslide hazard index (individual layer) to calculate distribution of exposed categories (population, built-up) across hazard thresholds (3 classes).
  
  - **Tropical cyclones** [[Procedure](procedures/Analytical_procedure_function.md) - [Notebook](notebooks/Tropical_cyclones.ipynb)] - uses wind hazard model (gust speed for 3 return periods) to calculate impact over built-up according to damage function.
  
  - **Air Pollution** [[Procedure](procedures/Analytical_procedure_classes.md) - [Notebook](notebooks/AirPollution.ipynb)] - uses PM2.5 hazard map (individual layer) to calculate health impact on population according to mortality function.

--------------------------------------

## CREDITS

Tools developed in the context of World Bank CCDR analytics
- Concept: [Mattia Amadio](https://www.github.com/matamadio)
- Coding: [Takuya Iwanaga](https://github.com/ConnectedSystems)
- Additional coding: [Arthur H. Essenfelder](https://github.com/artessen)
