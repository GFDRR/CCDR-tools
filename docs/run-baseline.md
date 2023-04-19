# Baseline risk

Once required input layers have been created according to [tool setup](tool-setup), the analysis can run.

Select the country of interest, the exposure category and the level of administrative boundaries aggregation.

```{figure} images/ccdr-nb_settings.png
---
align: center
---
Settings from one of the python notebooks
```

Note that not all combinations of hazards x exposure are supported; some are not covered by appropriate damage functions or classification (read [more](inro-risk)).
Select the analytical approach accordingly.

## Analytical approach: Expected Annual Impact
This approach uses a mathematical relationship to calculate impact over exposed categories (read [more](EAI)).
For example, flood hazard impact over population is calculated using a mortality function, while the impact over built-up uses a damage function for buildings.

The functions can be manually edited in the notebook, if a better model is available for the country of interest.

```
def damage_factor_builtup(x):
    """A polynomial fit to average damage across builtup land cover relative 
    to water depth in meters in Asia.

    The sectors are commercial, industry, transport, infrastructure and residential.

    Values are capped between 0 and 1, where water depth values >= 6m return a damage factor of 1

    References
    ----------
    .. [1] JRC, 2017
    """
    return np.maximum(0.0, np.minimum(1.0, -0.0028*x**3 + 0.0362*x**2 + 0.0095*x)) 	# Floods - AFRICA
    #return np.maximum(0.0, np.minimum(1.0, 0.9981236 - 0.9946279*np.exp(-1.711056*x))) # Floods - LAC
    #return np.maximum(0.0, np.minimum(1.0, 0.00723*x**3 - 0.1000*x**2 + 0.5060*x))	# Floods - ASIA
```

A minimum threshold can be set to ignore all values below - assuming that all risk is avoided under this threshold.

<img width=400 src="https://user-images.githubusercontent.com/44863827/156601233-8bb33d74-127a-4e60-93a3-0cc683d0efba.png">

A chart of the impact function can be generated in the interface for the selected exposure category.

<img width=400 src="https://user-images.githubusercontent.com/44863827/156601989-4997c63c-8c2a-4ce4-b6f9-bb7bb0506799.png">

If you want to inspect all steps of the processing, you can select the option to export all by-products as tiff files:

- [X] Export Intermediate rasters

```{figure} images/run-analysis.png
---
:width: 180px
:align: center
---
Click the button to start the processing
```

Once the run finishes, results are exported as geospatial data (.gpkg) and table (.csv).

By selecting

- [X] Preview results

A map will be generated at the end of the run, using a simple simbology.

<img width=700 src="https://user-images.githubusercontent.com/44863827/156605538-85af4764-a2cb-4d0f-8046-a59fdcbed50b.png">

The map can be zoomed and inspected with the pointer to show all the values in the table.

<img width=500 src="https://user-images.githubusercontent.com/44863827/156605784-b80e4ba8-aafd-4316-b9f8-d3657230a1d4.png">

EAI represents the aggregated absolute risk estimate:
 - **Fatalities** when considering impact over population;
 - **Hectars [ha] of built-up destroyed** when considering impact over built-up.
