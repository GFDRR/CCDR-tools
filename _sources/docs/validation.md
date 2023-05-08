# Validation and interpretation

[//]: # (Comment)

# Validate input
It is always a good practice to spend some time to evaluate the quality and representativeness of input data before diving into the analytics.
Input data can contain errors and artefacts; sometimes they are large and evident, sometimes they are small and hard to catch - but that doesn't mean they don't have an impact over the quality of results!

## Hazard

### Correct values interpretation and outliers

- Check layer projection sysyem (CRS)
- Check unit of measure (hazard metadata)
- Check values distribution (histogram)
- Set a proper cut for outliers before setting any hazard threshold or classification

### Geographic correlation

This is easier to check for hazards with strong dependency to the geomorphology, such as floods and landslides. An inspection of hazard layers against a reliable basemap (e.g. ESRI or Google) can help to spot inconsistencies between the representation of hazard distribution and its expected behaviour (rule of thumb) in relation to the basemap.

Some examples:
- River flood extent occurring too far from its catchment; depth values not matching with the elevation from digital terrain model.
- High landslide hazard on flat terrain.
- Coastal floods spreading for kilometers over the whole coastal plain; ignoring coastal defence measures.

### Validation against empirical datasets

Probabilistic scenarios of hazard data can be compared with observed disaster events to corroborate the analysis, although this is often a difficult task due to lack of granular spatial data representing the events. Some hazards are better covered by observations than others - see the [disaster records](disaster-data.md).

```{figure} images/hzd_validate.jpg
---
align: center
---
Example of flood model extent validation between observed events (Pakistan 2022) and probabilistic model (Fathom RP 1,000 years).
```

## Exposure

### Correct values interpretation and outliers

- Check layer projection sysyem (CRS)
- Check unit of measure (exposure metadata)
- Check values distribution (histogram)

### Comparison against basemap

Identify artifacts in exposure data; if the errors are limited and a better source of truth is available for comparison, fix them manually; else, account for them in the results interpretation and uncertainty.

### Cross-comparison between similar datasets

Run a statistical comparison between similar dataset to estimate their similarity.
An example is spatial correlation:

`Insert figure`

# Output interpretation
The analytical model produces numbers; then is to the ability of the risk analyst to interpret them correctly, spot errors, and build a narrative to make the results digestable for a non-expert audience.

## Validation against empirical disaster data

- First, check that results make sense in terms of metrics and units of measures.
  - Relative impacts over 100% are always a good indicator that something went wrong.
- Does the calculated distribution of risk reflect the historical distribution of disaster events as recorded by catalogues (e.g. EM-DAT) and agencies (e.g. reliefweb)?
  - If not, can you explain the reason?

## Uncertainty
In the development of risk models, many different data sets are used as input components. The level of uncertainty is directly linked to the quality of the input data. In addition, there is also random uncertainty that cannot be reduced. On many occasions during model development, expert judgment and proxies are used in the absence of historical data, and the results are very sensitive to most of these assumptions and variations in input data. As such, outputs of these models should be considered indicators of the order of magnitude of the risks, not as exact values. Better data quality and advances in science and modelling methodologies reduce the level of uncertainty, but it is crucial to interpret the results of any risk assessment against the backdrop of unavoidable uncertainty.

A risk model can produce a very precise result—it may show, for example, that a 1-in-100-year flood will affect 388,123 people—but in reality the accuracy of the model and input data may provide only an order of magnitude estimate. Similarly, sharply delineated flood zones on a hazard map do not adequately reflect the uncertainty associated with the estimate and could lead to decisions such as locating critical facilities just outside the flood line, where the actual risk is the same as if the facility was located inside the flood zone.

We should not be apprehensive of using information that is uncertain so long as any decisions and actions based upon the information are made with a full understanding of the associated uncertainty and its implications. It should be remembered that uncertainty will usually promote an analytical debate that should lead to robust decisions, which is a positive manifestation of uncertainty. Credible scientific results should also have associated uncertainty clearly presented.