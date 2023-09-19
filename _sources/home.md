# Climate & Disaster Risk Screening Tools

A collection of scripted tools developed to inform risk analytics for the the World Bank's [**Country Climate and Development Report**](https://www.worldbank.org/en/publication/country-climate-development-reports) risk screening activities (2022/2023).

The tools collected in this repository allow to:

- Perform spatial analytics of disaster risk for the present period ([**baseline**](docs/intro-risk#annual-risk-baseline)) based on global datasets
- Combine risk and poverty information into [**bi-variate maps**](docs/risk-poverty.md)
- Produce [**climate risk outlook**](docs/climate-risk.md) based on CMIP6 indices
- Present results into an interactive [**dashboard**](docs/presentation#dashboard)

```{note}
Are you a World Bank TTL? You can request for availability to produce a new country screening using [**this form**](https://forms.office.com/r/UU3LXBNz4T).
```

As an example of the output produced using these tools, check some of the risk screening reports produced (2022/2023):

- [**Cambodia**](https://github.com/GFDRR/CCDR-tools/blob/main/Top-down/reports/KHM_RSK.pdf)
- [**Senegal**](https://github.com/GFDRR/CCDR-tools/blob/main/Top-down/reports/Top-down/reports/SEN_RSK.pdf)
- [**OECS countries**](Top-down/reports/OECS_RSK.pdf)

Countries that have been already covered by the risk analytics:

<iframe src="docs/maps/CCDR_map.html" height="500" width="100%"></iframe>

```{table}
:name: vln-data
|**South & South-East Asia** | **West Africa & Sahel countries**| **Central & East Africa**  | **Latin America & Caribbean** |
|---|---|---|---|
| <ul><li>Pakistan<li>Nepal<li>Bangladesh<li>Cambodia<li>India</ul> | <ul><li>Ghana<li>Burkina Faso<li>Mali<li>Niger<li>Chad<li>Mauritania<li>Guinea-Bissau<li>Nigeria<li>Senegal</ul> | <ul><li>Ethiopia<li>Rwanda</ul> | <ul><li>Dominican Republic<li>Antigua & Barbuda<li>Dominica<li>Saint Kitts & Nevis<li>Saint Lucia<li>Grenada<li>Saint Vincent & Grenadines</ul> |
```

```{note}
This documentation specifically reflects the approches and methods adopted for the CCDR disaster risk screening following the [**CCDR guidance note**](https://github.com/GFDRR/CCDR-tools/blob/main/docs/CCDR_notes/CCDR%20Tools%20and%20Approaches.pdf). They are based on the most typical DRM framework, yet there are many alternative approaches that could be adopted for similar purposes.
Also note that our tools are not expected to reflect all existing risk perspectives and dimensions, rather producing standardised risk indicators.
```
The CCDR risk screening tools has been developed in agreement with regional geography and poverty teams, and with the support of the World Bank Global Facility for Disaster Risk and Recovery (**GFDRR**).

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
Conceptual framework of Disaster Risk as a combination of an hazard (described by intensity in relation to its occurrence frequency or probability) occurring in the same location of Exposed asset or capital (which can include population, built-up asset, or else) which is vulnerable to suffer impact from that specific hazard.
```

```{seealso}
The **UN Global Assessment Report on Disaster Risk Reduction (GAR)** is the flagship report of the United Nations on worldwide efforts to reduce disaster risk. The GAR is published by the UN Office for Disaster Risk Reduction (UNDRR), and is the product of the contributions of nations, public and private disaster risk-related science and research, amongst others.

- **[UNDRR GAR 2022](https://www.undrr.org/global-assessment-report-disaster-risk-reduction-gar)**
```