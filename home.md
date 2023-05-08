# Climate & Disaster Risk Screening Tools

A collection of scripted tools developed to inform risk analytics for the the World Bank's [**Country Climate and Development Report**](https://www.worldbank.org/en/publication/country-climate-development-reports) risk screening activities (2022/2023).

The tools collected in this repository allow to:

- Perform spatial analytics of disaster risk for the present period ([**baseline**](intro-risk#annual-risk-baseline)) based on global datasets
- Combine risk and poverty information into [**bi-variate maps**](risk-poverty.md)
- Produce [**climate risk outlook**](climate-risk.md) based on CMIP6 idnices
- Present results into an interactive [**dashboard**](presentation#dashboard)

As an example of the output produced using these tools, check some of the risk screening reports produced (2022/2023):

- [**Cambodia**](https://github.com/GFDRR/CCDR-tools/blob/main/Top-down/reports/KHM_RSK.pdf)
- [**Nigeria**](Top-down/reports/NGA_RSK.pdf)
- [**OECS countries**](Top-down/reports/OECS_RSK.pdf)

Other countries that were covered by the risk analytics:

**South & South-East Asia**
- Pakistan
- Nepal
- Bangladesh
- Cambodia
- India

**West Africa**
- Burkina Faso
- Mali
- Niger
- Chad
- Mauritania
- Guinea-Bissau
- Nigeria
- Senegal

**East & Central Africa** 
- Ethiopia
- Rwanda

**Latin America & Caribbean**
- Dominican Republic
- OECS countries (Antigua & Barbuda; Dominica; Saint Kitts & Nevis; Saint Lucia; Grenada; Saint Vincent & Grenadines)

```{note}
Tis documentation specifically reflects the approches and methods adopted for the CCDR disaster risk screening. They are based on the most typical DRM framework, yet there are many alternative approaches that could be adopted for similar purposes.
Also note that our tools are not expected to reflect all existing risk perspectives and dimensions, rather producing standardised risk indicators.
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