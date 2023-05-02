# Risk and poverty

Introduce bi-variate maps, examples.

The distributional impact of climate risks can be examined by overlaying poverty maps shown in Figure 21, on built-up asset and agricultural land EAE and EAI maps produced in the earlier section. These results are visualized using a series of bivariate maps that show the locations where risk is most likely to translate into severe impacts on the poorest and vulnerable households.



## Wealth indices

The estimate of poverty distribution is usually done measuring either the income distribution (of the household’s dwellers), or expenditure (average monthly expenditure of the household). However, due to the difficulties in obtaining reliable income/consumption data in low- and middle-income countries, alternative ways to build the wealth index are often the best available approximation of relative socio-economic status.
<br>
The presence of physical assets in the household can be used to construct a wealth index [(Filmer and Pritchett 2001)](https://www.jstor.org/stable/3088292). Relative wealth indices are an equally valid, but distinct measure of household socio-economic status from income and consumption measures [(Poirier et al. 2019)](https://doi.org/10.1007/s11205-019-02187-9). Context-specific factors such as country development level may affect the concordance of health and educational outcomes with wealth indices and urban–rural disparities can be more pronounced using wealth indices compared to income or consumption.

```{caution}
While the wealth quintiles are useful to understand relative wealth and equity within a country, they do not give one a sense of absolute wealth and neither comply with a predefined mathematical relationship; for instance, a tile with a wealth index value of **2** is richer than a tile with a value of **0.5**, but there is no information on how much richer. Someone deemed “rich” according to the wealth quintiles in developing countries might still have few resources for out-of-pocket expenditures.
```

```{table}
:name: vln-se
| **Name** | **Source** | **Model type** | **Scale** |
|---:|---:|---:|---:|---:|---:|
| [Relative Wealth Index](https://data.humdata.org/dataset/relative-wealth-index) | META | Wealth index | National |
| [Demographic Health Survey](https://dhsprogram.com/data/available-datasets.cfm) | USAID| Wealth index | National |
```

The USAID **Demographic Health Survey** (**DHS**) has been used to this purpose, analysing the quantiles distribution obtained from a series of questions about household construction materials, water and sanitation access, and ownership of various items (e.g. television, refrigerator), which form a relative indicator of socio-economic status within a given country at the time of the survey.

AI-based indices such as the **Relative Wealth Index** (**RWI**) [Chi et al. 2022](https://www.pnas.org/doi/10.1073/pnas.2113658119) are appealing due to the immediate and cost-effective estimates they can provide. The RWI is an index estimated by a machine learning model for 135 low and middle-income countries to provide micro-estimates (projections) of wealth and poverty at fine-grained 2.4 km resolution tiles. The model is trained on vast and heterogeneous datasets from satellites, mobile phone networks, topographic maps, as well as connectivity data from Facebook. The approach for creating the RWI map overcomes essential limitations of the traditional surveys, such as fine-grained coverage, and timely and cost-efficient data, while extending to countries where DHS does not operate. However, the application of RWI index to a real-world scenario would be sensitive to the socioeconomic particularities of the country, leading to significantly different estimates from the ones obtained by a traditional survey approach.

## Index normalisation

The DHS data are weighted to render the survey demographically representative; while the RWI requires to be weighted. The **High-Resolution Settlement Layer** [(**HRSL**)](https://arxiv.org/abs/1712.05839) is used to obtain the population estimates at 100 m resolution.

```{figure} images/rwi1.jpg
---
align: center
---
(left) Original RWI data points (x,y) from Meta; (right) RWI as regular grid (2.4 km).
```

```{figure} images/rwi2.jpg
---
align: center
---
(left) RWI weighted by population at 100 m (GHSL); (right) Population-weighted RWI summarised at ADM 3 level.
```

## Bi-variate maps

Poverty maps are combined with EAE/EAI maps to generate bi-variate maps. These maps provide ranks explained by a 3x3 matrix, resulting in 9 possible scores ranging from low-risk / low-poverty to high-risk / high poverty. The matrix is built by classifying poverty indicators into three quantiles and dividing risk indicators (EAE/EAI) of each hazard type into groups.

```{table}
:name: bivariate-matrix

|  **Risk indicator**  |  **Unit**  |  **Metric**  <td colspan=3>Risk Classification  |  |  |
|:---:|:---:|:---:|:---:|:---:|:---:|
|  |  |  | **Low** | **Medium** | **High** |
|  Flood x Population  |  EAI [#]  |  Total count  |  0.01 - 100  |  100 – 1,000  |  > 1,000  |
|  Flood x Built-up  |  EAI [Ha]  |  Total count  |  0.01 – 1  |  1 – 10  |  > 10  |
|  Flood x Agri land  |  EAE [Ha]  |  Total count  |  0.01 - 100  |  100 – 1,000  |  > 1,000  |
|  Drought x Agri land  |  EAI [%]  |  Ratio  |  1 - 5  |  5 - 15  |  > 15  |
|  Heat stress x Population  |  EAE [#]  |  Ratio  |  1 – 10,000  |  10,000 – 30,000  |  > 30,000  |
|  Air pollution x  Population  |  EAE [#]  |  Ratio  |  1 – 5,000  |  5,000 – 15,000  |  > 15,000  |
```

Classification of total exposure on an administrative unit is done both on the basis of absolute numbers or ratios. For instance, as severe fluvial flooding and landslides represent very localized threats, the classification is based on total counts. In comparison, heat waves, droughts and air pollution are more widespread across geographic units and therefore classified into groups based on proportions. 

How to create bi-variate maps, link to script
