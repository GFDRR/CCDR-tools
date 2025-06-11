# Hazard datasets

**Hazard datasets** refer to a variety of datasets that can be used to represent the value that is exposed to suffer damage and losses from natural hazards. This section presents some of the most common and recent type of data and indicators used for this purpose. Please note that _CCDR focus only on hydro-meteorological hazards_, as geopyhisical hazards occurrence and intensity are not affected by climate change.

```{seealso}
Hazard datasets developed by WB disaster risk projects have been placed in a special collection of the WB Development Data Hub: [Risk Data Library Collection: **HAZARD**](https://datacatalog.worldbank.org/search?fq=(identification%2Fcollection_code%2Fany(col:col%20eq%20%27RDL%27))&q=hazard).
```

The most relevant datasets (updated, high resolution, scientific quality) representing extreme events and long-term hazards that were considered for inclusion in the CCDR and other risk-related activities across the Bank have been reviewed, explaining their pros and cons and providing suggestions for their use. Most datasets only cover the historical period (*baseline*); while a few of the hydro-met hazards also offer some *hazard projections*.

Some hazards are modelled using a **probabilistic approach**, providing a set of scenarios linked to hazard frequency for the period of reference. For the current data availability, this is the case for floods, storm surges, cyclones, heatwaves, and wildfires.
Others, such as landslides, use a **deterministic approach**, providing an individual map of hazard intensity or susceptibility.

<style>
.hazard-table {
  width: 75%;
  margin: 2rem auto;
  border-collapse: collapse;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-radius: 12px;
  overflow: hidden;
  background: white;
}

.hazard-table th,
.hazard-table td {
  width: 33.33%;
}

.hazard-table th {
  color: white;
  padding: 1.5rem 1rem;
  text-align: center;
  font-size: 1.1rem;
  font-weight: 600;
  border: none;
}

.hazard-table th:nth-child(1) {
  background: linear-gradient(to bottom, #5d4037 0%, #8d6e63 100%);
}

.hazard-table th:nth-child(2) {
  background: linear-gradient(to bottom, #37474f 0%, #607d8b 100%);
}

.hazard-table th:nth-child(3) {
  background: linear-gradient(to bottom, #388e3c 0%, #66bb6a 100%);
}

.hazard-table th a {
  color: white;
  text-decoration: none;
  font-weight: 600;
}

.hazard-table th a:hover {
  text-decoration: underline;
}

.hazard-table td {
  padding: 1.5rem 1rem;
  text-align: center;
  vertical-align: middle;
  border: 1px solid #e8f4f8;
  background-color: #fafcfd;
  height: 160px;
}

.hazard-table tr:nth-child(even) td {
  background-color: #f8fbfc;
}

.hazard-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  height: 100%;
  justify-content: center;
}

.hazard-item a {
  color: #0b3860;
  text-decoration: none;
  font-weight: 500;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
}

.hazard-item a:hover {
  color: #fe5f86;
  transform: translateY(-2px);
  transform: scale(1.1);
}

.hazard-item img {
  width: 96px;
  height: 96px;
  object-fit: contain;
}

.hazard-text {
  font-size: 1.3rem;
  line-height: 1.3;
  text-align: center;
}

@media (max-width: 768px) {
  .hazard-table {
    width: 95%;
    font-size: 0.8rem;
  }
  
  .hazard-table th, 
  .hazard-table td {
    padding: 1rem 0.5rem;
  }
  
  .hazard-item img {
    width: 80px;
    height: 80px;
  }
}
</style>

<table class="hazard-table">
<thead>
<tr>
<th><a href="hzd_gp-data.md"><strong>GEOPHYSICAL</strong></a></th>
<th><a href="hzd_hm-data.md"><strong>HYDRO-METEOROLOGICAL</strong></a></th>
<th><a href="hzd_env-data.md"><strong>ENVIRONMENTAL</strong></a></th>
</tr>
</thead>
<tbody>
<tr>
<td>
<div class="hazard-item">
<a href="hzd_gp_eq">
<div class="hazard-text">Earthquake</div>

![Earthquake](images/hzd_icons/earthquake.png)

</a>
</div>
</td>
<td>
<div class="hazard-item">
<a href="hzd_hm_fl">
<div class="hazard-text">River floods</div>

![River flood](images/hzd_icons/flood.png)

</a>
</div>
</td>
<td>
<div class="hazard-item">
<a href="hzd_env_ap">
<div class="hazard-text">Air pollution</div>

![Air pollution](images/hzd_icons/air-pollution.png)

</a>
</div>
</td>
</tr>
<tr>
<td>
<div class="hazard-item">
<a href="hzd_gp_ts">
<div class="hazard-text">Tsunami</div>

![Tsunami](images/hzd_icons/tsunami.png)

</a>
</div>
</td>
<td>
<div class="hazard-item">
<a href="hzd_hm_ls">
<div class="hazard-text">Landslide</div>

![Landslide](images/hzd_icons/landslide.png)

</a>
</div>
</td>
<td></td>
</tr>
<tr>
<td>
<div class="hazard-item">
<a href="hzd_gp_vo">
<div class="hazard-text">Volcanic activity</div>

![Volcanic activity](images/hzd_icons/volcano.png)

</a>
</div>
</td>
<td>
<div class="hazard-item">
<a href="hzd_hm_ss">
<div class="hazard-text">Coastal flood</div>

![Coastal flood](images/hzd_icons/storm-surge.png)

</a>
</div>
</td>
<td></td>
</tr>
<tr>
<td></td>
<td>
<div class="hazard-item">
<a href="hzd_hm_tc">
<div class="hazard-text">Tropical cyclones</div>

![Tropical cyclones](images/hzd_icons/wind.png)

</a>
</div>
</td>
<td></td>
</tr>
<tr>
<td></td>
<td>
<div class="hazard-item">
<a href="hzd_hm_dr">
<div class="hazard-text">Drought</div>

![Drought](images/hzd_icons/drought.png)

</a>
</div>
</td>
<td></td>
</tr>
<tr>
<td></td>
<td>
<div class="hazard-item">
<a href="hzd_hm_hs">
<div class="hazard-text">Heat stress</div>

![Heat stress](images/hzd_icons/heat-wave.png)

</a>
</div>
</td>
<td></td>
</tr>
</tbody>
</table>