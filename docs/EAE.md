# Expected Annual Exposure (EAE) 

The script performs combination of hazard and exposure geodata from global datasets according to user input and settings, and returns a risk score in the form of Expected Annual Exposure (EAE) for the baseline (reference period). 

The "classes" approach simply split the hazard intensity layer into classes and, for ach one, calculates the toal exposure for the selected category. 
For example, flood hazard over agriculture is measured in terms of hectars of land falling within different intervals of water depth.
Note that Minimum threshold is deactivated/ignored for this approach.

The spatial information about hazard and exposure is first collected at the grid level, the output is then aggregated at ADM2 boundary level to combine Vulnerability scores and calculate risk estimate. This represents the disaster risk historical baseline.


- LOOP over each hazard RPi layers:
  - Classify hazard layer RPi according to settings: number and size of classes: `RPi` -> `RPi_Cj` (multiband raster)
  - Each class `Cj` of RPi is used to mask the Exposure layer -> `RPi_Cj_Exp` (multiband raster)
  - Perform zonal statistic (SUM) for each ADMi unit over eac `RPi_Cj_Exp` -> `table [ADMi_NAME;RPi_C1_Exp;RPi_C2_Exp;...RPi_Cj_Exp]`<br>
    Example using 3 RP scenarios: (10-100-1000) and 3 classes (C1-3): `table [ADM2_NAME;RP10_C1_Exp;RP10_C2_Exp;RP10_C3_Exp;RP100_C1_Exp;RP100_C2_Exp;RP100_C3_Exp;RP1000_C1_Exp;RP1000_C2_Exp;RP1000_C3_Exp;]

- Calculate EAE
  - Calculate the exceedance frequency for each RPi -> `RPi_ef = (1/RPi - 1/RPi+1)` where `RPi+1` means the next RP in the serie.
    Example using 3 RP scenarios: RP 10, 100, and 1000 years. Then: `RP10_ef = (1/10 - 1/100) = 0.09`
  - Multiply exposure for each scenario i and class j `(RPi_Cj_Exp)` with its exceedence frequency `(RPi_ef)` -> `RPi_Cj_Exp_EAE`
  - Sum `RPi_Cj_Exp_EAE`across multiple RPi for the same class Cj -> `table [ADMi;Cj_Exp_EAE]`<br>
    Example using 3 classes (C1-3): `table [ADMi;C1_Exp_EAE;C2_Exp_EAE;C3_Exp_EAE]`

	| RP | Exceedance freq | C3 | C4 | C5 | C6 | C3-6 | C3_EAE | C4_EAE | C5_EAE | C6_EAE | C3-6_EAE |
	|:---:|---|:---:|:---:|:---:|:---:|---|:---:|:---:|:---:|:---:|---|
	| 10 | 0.09 | 4,036 | 1,535 | 2,111 | 1,967 | 9,658 | 363 | 138 | 190 | 177 | 868 |
	| 100 | 0.009 | 8,212 | 5,766 | 5,007 | 13,282 | 32,367 | 739 | 519 | 451 | 1,195 | 2,904 |
	| 1000 | 0.0009 | 8,399 | 5,134 | 4,371 | 25,989 | 44,893 | 756 | 462 | 393 | 2,339 | 3,950 |
	| Total | | | | | | | 1,858 | 1,119 | 1,034 | 3,711 | 7,723 |
  
  - Plot Exceedance Frequency Curve. Example:<br>
    ![immagine](https://user-images.githubusercontent.com/44863827/198069028-8bd0e317-0b2e-4a22-b912-e260d3b3bd65.png)
  - Perform zonal statistic of Tot_Exp using ADMi -> `[ADMi;ADMi_Exp;Exp_EAE]` in order to calculate `Exp_EAE% = Exp_EAE/ADMi_Exp` -> `[ADMi;ADMi_Exp;Exp_EAE;Exp_EAE%]`


