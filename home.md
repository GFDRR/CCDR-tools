# Risk Data Library - Country Climate & Disaster Risk Screening Tools

This documentation offers guidance on risk screening and provides pythons tools to quickly produce natual hazards' risk screening at the national or sub-national level. The tools have originally being created for the World Bank's [**Country Climate and Development Report**](https://www.worldbank.org/en/publication/country-climate-development-reports) risk screening activities (2022/2024) and then furtherly developed within the [**Risk Data Library project**](docs/rdl.md).

The CCDR toolkit allow to perform spatial analytics of disaster risk based on global datasets.
Additionally, it offers open-source approaches and methods to:
- Combine risk and poverty information into [**bi-variate maps**](docs/risk-poverty.md)
- Produce [**climate risk outlook**](docs/climate-risk.md) based on CMIP6 indices
- Present results into an interactive [**dashboard**](https://matamadio.github.io/CCDR-geoboard)

```{note}
Are you a World Bank TTL? You can request for availability to produce a new country screening using [**this form**](https://forms.office.com/r/UU3LXBNz4T).
```
The map shows countries that have been already covered by the risk analytics. Click on the country name to download the risk screening report.

<iframe src="docs/maps/CCDR_map.html" height="500" width="100%"></iframe>

<!-- Table of CCDR Countries -->
| South & South-East Asia | Africa | Latin America & Caribbean | East Asia and Pacific |
|-------------------------|--------------------------------|------------------------|----------------------------|
| - Pakistan<br>- Nepal<br>- Bangladesh<br>- [**Cambodia**](https://github.com/GFDRR/CCDR-tools/blob/dev_push/reports/KHM_RSK.pdf)<br>- India<br>- Thailand<br>- Malaysia<br>- Philippines<br>- Mongolia | - Ghana<br>- Burkina Faso<br>- Mali<br>- Niger<br>- Chad<br>- Mauritania<br>- Guinea-Bissau<br>- Nigeria<br>- [**Senegal**](https://github.com/GFDRR/CCDR-tools/blob/dev_push/reports/SEN_RSK.pdf)<br>- Ethiopia | - Dominican Republic<br>- [**OECS countries**](https://github.com/GFDRR/CCDR-tools/blob/dev_push/reports/OECS_RSK.pdf)<br>&nbsp;&nbsp;- Antigua & Barbuda<br>&nbsp;&nbsp;- Dominica<br>&nbsp;&nbsp;- Saint Kitts & Nevis<br>&nbsp;&nbsp;- Saint Lucia<br>&nbsp;&nbsp;- Grenada<br>&nbsp;&nbsp;- Saint Vincent & Grenadines | - Fiji |

```{note}
This documentation reflects the approches and methods adopted for the CCDR disaster risk screening following the [**CCDR guidance note**](https://github.com/GFDRR/CCDR-tools/blob/main/docs/CCDR_notes/CCDR%20Tools%20and%20Approaches.pdf). They are based on the most typical DRM framework, yet there are many alternative approaches that could be adopted for similar purposes.
Also note that our tools are not expected to reflect all existing risk perspectives and dimensions, rather producing standardised risk indicators.
```
The CCDR risk screening tools has been developed in agreement with regional geography and poverty teams, and with the support of the World Bank Global Facility for Disaster Risk and Recovery ([**GFDRR**](https://www.gfdrr.org)).

```{figure} docs/images/GFDRR_logo.png
---
align: center
width: 70%
---
```

## Disaster risk framework

In the field of Disaster Risk Management (DRM), Risk (**R**) is typically calculated as a function of: the hazard occurrence probability and intensity (i.e., physical magnitude) in a particular location (**H**, for Hazard); the people and physical assets (infrastructure, buildings, crops, etc.) situated in that location and therefore exposed to the hazard (**E**, for Exposure); and the conditions determined by physical, social, and economic factors which increase the susceptibility of an exposed individual, community, asset or system to the impacts of hazards (**V**, for Vulnerability).

```{figure} docs/images/risk_framing.png
---
align: center
---
Conceptual framework of Disaster Risk as a combination of an hazard (described by intensity in relation to its occurrence frequency or probability) occurring in the same location of Exposed asset or capital (can include population, built-up asset, or else) which is vulnerable to suffer impact from that specific hazard.
```

```{seealso}
The **UN Global Assessment Report on Disaster Risk Reduction (GAR)** is the flagship report of the United Nations on worldwide efforts to reduce disaster risk. The GAR is published by the UN Office for Disaster Risk Reduction (UNDRR), and is the product of the contributions of nations, public and private disaster risk-related science and research, amongst others.

- **[UNDRR GAR 2022](https://www.undrr.org/global-assessment-report-disaster-risk-reduction-gar)**
```
