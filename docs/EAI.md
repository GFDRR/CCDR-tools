# Expected Annual Impact (EAI) 

This analytical approach applies to multiple probabilistic hazard scenarios and aims to produce a mean estimate of Expected Annual Impact (EAI) over exposed categories.

The EAI is calculated by multiplying the impact from each scenario with its exceedance probability, and then summing up to obtain the mean annual risk considering the whole range of hazard occurrence probabilities. The exceedance frequency curve highlights the relationship between the return period of each hazard and the estimated impact: the area below the curve represents the total annual damage considering all individual scenario probabilities.
<div align=center>
<img src="https://user-images.githubusercontent.com/44863827/201917310-9fc8b871-8351-4657-959e-d09c0b0e340c.png">
</div>

## OBJECTIVE

The script performs combination of hazard and exposure geodata from global datasets according to user input and settings, and returns a risk score in the form of Expected Annual Impact (EAI) for baseline (reference period). 
The spatial information about hazard and exposure is first combined at the grid level, then the total risk estimate is calculated at ADM boundary level. This represents the disaster risk historical baseline.
The output is exported in form of tables, statistics, charts (excel format) and maps (geopackage).

## SCRIPT OVERVIEW

- Script runs on one country, one hazard at time to keep the calculation time manageable.
- The analysis is carried at the resolution of the exposure layer. E.g. when using Worldpop exposure layer, it is 100x100 meters.
- User input is required to define country, exposure layer, and settings.
- Settings affect how the processing runs (min theshold).
- The core of the analysis is raster calculation, combinining exposure and hazard value through an impact function.
- The information is then aggregated at ADM level using zonal statistic.
- The expected annual impact (EAI) is computed by multiplying the impact value with its exceedence frequency (1/RPi - 1/RPj) depending on the scenario. The exceedance frequency curve (EFC) is plotted.
- Table results are exported in excel format, map rsults are exported in gpkg format.

## DATA MANAGEMENT

- Load country boundaries for multiple administrative levels sourced from [HDX](https://data.humdata.org/dataset) or [Geoboundaries](https://www.geoboundaries.org). Note that oftern there are several versions for the same country, so be sure to use the most updated from official agencies (eg. United Nations).

- Verify that shapes, names and codes are consistent across different levels.

- Load exposure data
  - Population: WorldPop 2020 Population counts / Constrained individual countries, UN adjusted (100 m resolution)
	-  [Download page](https://hub.worldpop.org/geodata/listing?id=79)
	-  API according to ISO3 code e.g. `https://www.worldpop.org/rest/data/pop/wpgp?iso3=NPL`
    	returns a Json that includes [the url of data](https://data.worldpop.org/GIS/Population/Global_2000_2020/2020/NPL/npl_ppp_2020.tif). 
  - Built-up: the latest [World Settlement footprint](https://download.geoservice.dlr.de/WSF2019/#details) can be download as tiles for the area of interest and merged into one compressed tif. 10 m binary grid can be resampled into 100 m using "mean": returns a 0-1 ratio describing the share of builtup for 100m cell.
  	- Download all tiles within country extent and merge them in a virtual raster (0-255)
  	- GDAL Warp on virtual raster, setting resolution = cell_res * 10
  	- GDAL Calc on Reprojected, setting calc: A/255
  - Land cover / Agricultural land: many are available from [planeterycomputer catalog](https://planetarycomputer.microsoft.com/catalog#Land%20use/Land%20cover). ESA 2020 at 10m resolution is suggested. Specific land cover types can be filtered using pixel value.

- Load hazard data.
	- Most hazard data consist of multiple layers (Return Periods, RP) each representing one probabilistic intensity maximum, or in other words the intensity of the hazard in relation to its frequency of occurrence.
	- Some hazards, however, comes as individual layers representing a mean hazard value. In this case, ignore the looping over RP.

## DATA PROCESSING

- LOOP over each hazard RPi layers:
  - Filter hazard layer according to settings (min and max thresholds) for each RPi -> `RPi_filtered`
  - Transform hazard intensity value into impact factor using specific hazard impact function or table: `RPi_filtered` -> `RP_IF`
  - RPi_IF is multiplied with the exposure layer to obtain expected impact: `RPi_IF` -> `RPi_exp_imp`
  - Perform zonal statistic (SUM) for each ADMi unit over every RPi_exp_imp -> `table [ADMi_NAME;RPi_exp_imp]`
    <br> e.g. `[ADM2_NAME;RP10_exp_imp;RP100_exp_imp;RP1000_exp_imp]`<br><br>

  <div align=center>
  <img src="https://user-images.githubusercontent.com/44863827/201050148-5aa6ad10-44b2-480f-9bef-51c3703d0e33.png">
  </div>

- Calculate EAI
  - Calculate the exceedance frequency for each RPi -> `RPi_ef = (1/RPi - 1/RPj)` where `j` is the next RP in the serie.
    Example using 3 scenarios: RP 10, 100, and 1000 years. Then: `RP10_ef = (1/10 - 1/100) = 0.09`
  - Multiply impact on exposure for each scenario `(RPi_Exp_imp)` with its exceedence frequency `(RPi_ef)` -> `RPi_Exp_EAI`
  - Sum all `RPi_exp_EAI` columns for each ADMi -> `table [ADMi;Exp_EAI]`

	| RP | Freq | Exceedance freq | Impact | EAI |
	|:---:|:---:|:---:|:---:|:---:|
	| 10 | 0.100 | 0.09 | 193 | 17 |
	| 100 | 0.010 | 0.009 | 1,210 | 11 |
	| 1000 | 0.001 | 0.001 | 3,034 | 3 |
	| Total |   |   |   | **31** |
  
  - Plot Exceedance Frequency Curve. Example:<br>
    ![immagine](https://user-images.githubusercontent.com/44863827/201049813-008d5fbc-3195-4289-ba18-34a126fe434e.png)
  - Perform zonal statistic of Tot_Exp using ADMi -> `[ADMi;ADMi_Exp;Exp_EAI]` in order to calculate `Exp_EAI% = Exp_EAI/ADMi_Exp` -> `[ADMi;ADMi_Exp;Exp_EAI;Exp_EAI%]`

## PREVIEW RESULTS
- Plot map of ADMi_EAI and related tables/Charts

  <div align=center>
  <table><tr><td width="45%"><img src="https://user-images.githubusercontent.com/44863827/201054765-5a1ce2c9-0bde-4e98-80ce-ee30ccefc4e2.png"></td>
	  <td><img src="https://user-images.githubusercontent.com/44863827/201055152-28482f07-7215-4b09-b3c2-397381d516af.png"></td></tr></table>
  </div>