# Risk Data Library - Country Climate & Disaster Risk Screening Tools

<div class="news-container">
    <div class="news-ticker">
        <span class="news-item"><strong>BIG UPDATE:</strong> New notebooks! New documentation! New video-tutorials! </span>
        <span class="news-item"><strong>BIG UPDATE:</strong> New notebooks! New documentation! New video-tutorials! </span>
        <span class="news-item"><strong>BIG UPDATE:</strong> New notebooks! New documentation! New video-tutorials! </span>
        <span class="news-item"><strong>BIG UPDATE:</strong> New notebooks! New documentation! New video-tutorials! </span>
    </div>
</div>

<style>
    .news-container {
        width: 100%;
        background-color: #f0f7fa;
        overflow: hidden;
        margin: 10px 0 20px 0;
        border-radius: 4px;
        border-left: 4px solid #118AB2;
    }
    .news-ticker {
        white-space: nowrap;
        padding: 10px 0;
        animation: ticker 30s linear infinite;
        color: #333;
        font-size: 14px;
    }
    @keyframes ticker {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    .news-item {
        display: inline-block;
        padding: 0 30px;
    }
    .news-item strong {
        color: #118AB2;
        font-weight: bold;
    }
    /* Pause animation on hover */
    .news-container:hover .news-ticker {
        animation-play-state: paused;
    }
</style>

This documentation offers guidance on risk screening and provides pythons tools to quickly produce natual hazards' risk screening at the national or sub-national level. The tools have originally being created for the World Bank's [**Country Climate and Development Report**](https://www.worldbank.org/en/publication/country-climate-development-reports) risk screening activities (2022/2025) and then furtherly developed within the [**Risk Data Library project**](docs/rdl.md).

## What you can do with these tools

<style>
.tools-grid {
  margin: 2rem 0;
}
.tool-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 2.5rem;
  gap: 1.5rem;
}
.tool-image {
  width: 250px;
  height: 250px;
  flex-shrink: 0;
  background-color: #064660;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  transition: background-color 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
}
.tool-image:hover {
  background-color: #fe5f86;
}
.tool-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}
.tool-content {
  flex: 1;
  padding-top: 0.5rem;
}
.tool-content h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.2rem;
}
.tool-content p {
  margin: 0;
  line-height: 1.6;
}
@media (max-width: 768px) {
  .tool-item {
    flex-direction: column;
    text-align: center;
  }
  .tool-image {
    width: 200px;
    height: 200px;
    margin: 0 auto;
  }
}
</style>


<div class="tools-grid">

<div class="tool-item">
<div class="tool-image">

![Disaster Risk Analysis](docs/images/rdl-disaster-risk-logo.png)

</div>
<div class="tool-content">
<h3><strong>Analyze disaster risk</strong></h3>
<p>Perform <strong><a href="https://gfdrr.github.io/CCDR-tools/docs/intro-risk.html">spatial analytics of disaster risk</a></strong> using globally available datasets.</p>
</div>
</div>

<div class="tool-item">
<div class="tool-image">

![Risk and Poverty Mapping](docs/images/rdl-risk-poverty-logo.png)

</div>
<div class="tool-content">
<h3><strong>Map the interaction of risk and poverty</strong></h3>
<p>Combine hazard exposure and socio-economic vulnerability to produce <strong><a href="docs/risk-poverty.html">bi-variate maps</a></strong> highlighting risk-poverty hotspots.</p>
</div>
</div>

<div class="tool-item">
<div class="tool-image">

![Future Climate Risk](docs/images/rdl-climate-risk-logo.png)

</div>
<div class="tool-content">
<h3><strong>Explore future climate risk</strong></h3>
<p>Generate climate risk outlooks based on <strong><a href="docs/climate-risk.html">CMIP6 climate projections</a></strong> and standardized risk indices.</p>
</div>
</div>

<div class="tool-item">
<div class="tool-image">

![Interactive Dashboards](docs/images/rdl-dashboard-logo.png)

</div>
<div class="tool-content">
<h3><strong>Build interactive dashboards</strong></h3>
<p>Present results in an <strong><a href="docs/presentation.html#dashboard">interactive dashboard</a></strong> format to support communication, exploration, and stakeholder engagement.</p>
</div>
</div>

</div>


```{note}
Are you a World Bank TTL? You can request for availability to produce a new country screening using [**this form**](https://forms.office.com/r/UU3LXBNz4T).
```

## Applied globally
The map shows countries that have been already covered by the risk analytics. Click on the country name to download the risk screening report.

<iframe src="docs/maps/CCDR_map.html" height="500" width="100%"></iframe>

<style>
.ccdr-countries-table {
  width: 100%;
  border-collapse: collapse;
  margin: 2rem 0;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-radius: 12px;
  overflow: hidden;
  background: white;
}

.ccdr-countries-table th {
  color: white;
  padding: 1.5rem 1rem;
  text-align: center;
  font-size: 1.1rem;
  font-weight: 600;
  border: none;
}

.ccdr-countries-table th:nth-child(1) {
  background: linear-gradient(to bottom, #ed9c00 0%, #503b2f 100%);
}

.ccdr-countries-table th:nth-child(2) {
  background: linear-gradient(to bottom, #c34919 0%, #3b0000 100%);
}

.ccdr-countries-table th:nth-child(3) {
  background: linear-gradient(to bottom, #2aa332 0%, #21320b 100%);
}

.ccdr-countries-table th:nth-child(4) {
  background: linear-gradient(to bottom, #69b6f6 0%, #102f48 100%);
}

.ccdr-countries-table td {
  padding: 1.5rem 1rem;
  vertical-align: top;
  border: none;
  border-right: 1px solid #e8f4f8;
  background-color: #fafcfd;
  width: 25%;
}

.ccdr-countries-table td:last-child {
  border-right: none;
}

.ccdr-countries-table tr:nth-child(even) td {
  background-color: #f8fbfc;
}

.country-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.country-list li {
  padding: 0.4rem 0;
  position: relative;
  padding-left: 1.2rem;
}

.country-list li:before {
  content: "▸";
  color: #fe5f86;
  font-weight: bold;
  position: absolute;
  left: 0;
}

.country-list li.sub-country {
  padding-left: 2.4rem;
  font-size: 0.95rem;
  color: #666;
}

.country-list li.sub-country:before {
  content: "▪";
  color: #999;
  left: 1.2rem;
}

.country-list a {
  color: #0b3860;
  text-decoration: none;
  font-weight: 600;
  border-bottom: 2px solid transparent;
  transition: all 0.2s ease;
}

.country-list a:hover {
  color: #fe5f86;
  border-bottom-color: #fe5f86;
}

@media (max-width: 768px) {
  .ccdr-countries-table {
    font-size: 0.9rem;
  }
  
  .ccdr-countries-table th, 
  .ccdr-countries-table td {
    padding: 1rem 0.5rem;
  }
  
  .ccdr-countries-table th {
    font-size: 1rem;
  }
}
</style>

<!-- Table of CCDR Countries -->
<table class="ccdr-countries-table">
<thead>
<tr>
<th>South & South-East Asia</th>
<th>Africa</th>
<th>Latin America & Caribbean</th>
<th>East Asia and Pacific</th>
</tr>
</thead>
<tbody>
<tr>
<td>
<ul class="country-list">
<li>Pakistan</li>
<li>Nepal</li>
<li>Bangladesh</li>
<li><a href="https://github.com/GFDRR/CCDR-tools/blob/main/reports/KHM_RSK.pdf"><strong>Cambodia</strong></a></li>
<li>India</li>
<li>Thailand</li>
<li>Malaysia</li>
<li>Philippines</li>
<li>Mongolia</li>
</ul>
</td>
<td>
<ul class="country-list">
<li>Ghana</li>
<li>Burkina Faso</li>
<li>Mali</li>
<li>Niger</li>
<li>Chad</li>
<li>Mauritania</li>
<li>Guinea-Bissau</li>
<li>Nigeria</li>
<li><a href="https://github.com/GFDRR/CCDR-tools/blob/main/reports/SEN_RSK.pdf"><strong>Senegal</strong></a></li>
<li>Ethiopia</li>
</ul>
</td>
<td>
<ul class="country-list">
<li>Dominican Republic</li>
<li><a href="https://github.com/GFDRR/CCDR-tools/blob/main/reports/OECS_RSK.pdf"><strong>OECS countries</strong></a></li>
<li class="sub-country">Antigua & Barbuda</li>
<li class="sub-country">Dominica</li>
<li class="sub-country">Saint Kitts & Nevis</li>
<li class="sub-country">Saint Lucia</li>
<li class="sub-country">Grenada</li>
<li class="sub-country">Saint Vincent & Grenadines</li>
</ul>
</td>
<td>
<ul class="country-list">
<li>Fiji</li>
</ul>
</td>
</tr>
</tbody>
</table>

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

```{raw} html
<style>
  .risk-diagram {
    text-align: center; 
    margin: 20px 0;
  }
  
  .risk-container {
    position: relative;
    width: 100%;
    max-width: 500px;
    height: 400px;
    display: inline-flex;
    justify-content: center;
    align-items: center;
    margin: 0 auto;
  }

  .risk-diagram svg {
    width: 100%;
    height: 100%;
    max-width: 100%;
    max-height: 100%;
  }

  .risk-section {
    transition: transform 0.3s ease, filter 0.3s ease, z-index 0.1s ease;
    cursor: pointer;
    transform-origin: center;
    z-index: 1;
  }

  .risk-section:hover {
    transform: scale(1.06);
    filter: drop-shadow(0 0 12px rgba(0, 0, 0, 0.3));
    z-index: 10;
  }

  .risk-section-text {
    pointer-events: none;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-weight: bold;
    font-size: 90px;
    text-anchor: middle;
    dominant-baseline: central;
    transition: font-size 0.3s ease;
  }

  .risk-tooltip {
    position: fixed;
    background: rgba(0, 0, 0, 0.92);
    color: white;
    padding: 12px 16px;
    border-radius: 8px;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.2s;
    z-index: 1000;
    font-size: 13px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
    max-width: 280px;
    line-height: 1.4;
  }
  
  .risk-tooltip h4 {
    margin: 0 0 8px 0;
    font-size: 14px;
    font-weight: bold;
    color: #fff;
  }
  
  .risk-tooltip ul {
    margin: 0;
    padding-left: 16px;
    list-style-type: disc;
  }
  
  .risk-tooltip li {
    margin: 4px 0;
    font-size: 12px;
  }

  /* Responsive adjustments */
  @media (max-width: 600px) {
    .risk-section-text {
      font-size: 70px;
    }
    .risk-container {
      height: 300px;
      max-width: 400px;
    }
  }
</style>

<div class="risk-diagram">
  <div class="risk-tooltip" id="riskTooltip"></div>
  <div class="risk-container">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" preserveAspectRatio="xMidYMid meet">
      <!-- Hazard (Blue) -->
      <g class="risk-section" data-info="<h4>Hazard</h4>Physical events with the potential to cause impacts over exposure<ul><li>Natural or human-induced phenomena</li><li>Examples: earthquakes, floods, storms</li><li>Characterized by intensity and frequency</li></ul>">
        <path d="M505.5 942.9 c-59.7 -3.6 -114 -47.1 -156 -125 -5.9 -10.9 -21.5 -43.8 -21.5 -45.4 0 -0.3 -0.9 -2.4 -1.9 -4.8 -2.9 -6.4 -12.5 -35.6 -16.5 -50.3 -7 -25.4 -13.4 -59.9 -16 -86.4 -1.7 -16.5 -4 -56.9 -3.3 -57.7 0.3 -0.2 3.1 1.1 6.3 2.9 9.8 5.5 35.6 17.4 50.1 23.2 58.7 23.1 126.4 34.1 188.4 30.7 21.4 -1.2 46 -3.9 60.9 -6.6 23.5 -4.4 62.3 -15.9 84.3 -24.9 14.5 -5.9 39.7 -17.5 48.2 -22.1 l8 -4.4 -0.3 13.2 c-2.2 109.2 -38.2 217.5 -96.7 290.2 -23.5 29.3 -55.7 53.2 -83.4 61.9 -15.7 4.9 -31.3 6.6 -50.6 5.5z" fill="#007fc3" />
        <text x="510" y="750" class="risk-section-text" fill="white">H</text>
      </g>
      
      <!-- Exposure (Teal) -->
      <g class="risk-section" data-info="<h4>Exposure</h4>Location and value of physical assets<ul><li>People, property and systems location</li><li>Economic value of exposed assets</li></ul>">
        <path d="M259.5 534.2 c-31.3 -21.1 -55 -40.7 -82.6 -68.2 -28.2 -28.1 -44.1 -47.4 -63.2 -76.6 -15.2 -23.2 -24.3 -40 -33.1 -61 -2.6 -6 -5.1 -11.8 -5.5 -12.9 -0.5 -1.1 -2.1 -5.6 -3.6 -10 -23.1 -69.5 -11 -132.6 32.5 -169 23.2 -19.3 54.5 -32.8 91.5 -39.2 14.2 -2.5 59.8 -2.5 77.5 0 27 3.7 62 11.2 81.2 17.3 11 3.5 41 14.5 49 18 30.9 13.5 63.3 31.6 87.1 48.6 l4.7 3.5 -10.2 7.9 c-43.8 33.7 -83.7 73.5 -113.3 112.9 -27.7 36.9 -45.1 66.5 -60.2 102.5 -19 45.1 -29.4 81.9 -36.8 130.8 -0.4 2.3 -1 4.2 -1.3 4.2 -0.4 0 -6.5 -4 -13.7 -8.8z" fill="#00cbab" />
        <text x="235" y="260" class="risk-section-text" fill="white">E</text>
      </g>
      
      <!-- Risk (Red) -->
      <g class="risk-section" data-info="<h4>Risk</h4>Chance of exposed assets to suffer impact from hazard <ul><li>Physical, social, economic losses</li><li>Direct and indirect damages</li><li>Recovery time and costs</li></ul>">
        <path d="M489 612.9 c-51.8 -2.4 -111.5 -17.7 -162 -41.5 -25.8 -12.2 -37 -18.5 -37 -20.8 0 -4.1 4.1 -28.3 7.1 -42.6 3.5 -16.3 12 -46.5 17.3 -61.3 17.4 -48.2 39.3 -88.6 71 -131 26.9 -36 71.4 -79.7 114.7 -112.8 l11.7 -8.8 5.5 3.9 c33.1 23.1 77.5 63.5 103.4 94 9.8 11.6 27.8 35.3 36 47.5 39 58.1 66.6 129.3 75.7 195.5 0.9 6.3 1.8 12.7 2.1 14.2 0.4 2.6 -0.2 3.2 -7.3 7.3 -33.6 19.9 -89.5 40.8 -131.7 49.4 -13 2.6 -42.5 5.9 -59 6.6 -27.4 1.1 -31.5 1.2 -47.5 0.4z" fill="#f3436a" />
        <text x="510" y="420" class="risk-section-text" fill="white">R</text>
      </g>
      
      <!-- Vulnerability (Yellow) -->
      <g class="risk-section" data-info="<h4>Vulnerability</h4>Susceptibility of exposed elements to suffer damage<ul><li>Physical fragility</li><li>Socio-economic factors</li><li>Lack of resilience and coping capacity</li></ul>">
        <path d="M750.5 538.7 c-8.3 -55.4 -23 -103.3 -46.4 -152.2 -12.3 -25.7 -28.8 -52.3 -49.6 -79.8 -16 -21.3 -25.1 -32.1 -42.6 -50.1 -25.5 -26.3 -54.3 -51.7 -77.7 -68.3 l-4.3 -3.1 4.3 -3.4 c22.2 -17.7 67.1 -42.5 101.8 -56.1 68.6 -27.1 144.4 -37.2 198.2 -26.6 26.4 5.2 54 16.3 74.2 29.6 15.5 10.3 31.8 28.8 40.3 45.7 23.8 47.3 18.7 105.9 -15.3 173.8 -21.8 43.6 -48 79.4 -86.4 117.9 -27.8 28 -59.4 53.6 -90.2 73.2 l-5.6 3.6 -0.7 -4.2z" fill="#ffc757" />
        <text x="780" y="260" class="risk-section-text" fill="white">V</text>
      </g>
    </svg>
  </div>
</div>

<script>
  (function() {
    const tooltip = document.getElementById('riskTooltip');
    const sections = document.querySelectorAll('.risk-section');

    sections.forEach(section => {
      section.addEventListener('mousemove', e => {
        tooltip.innerHTML = section.dataset.info;
        
        // Position tooltip near mouse cursor
        const x = e.clientX + 15;
        const y = e.clientY - 10;
        
        // Keep tooltip within viewport bounds
        const tooltipRect = tooltip.getBoundingClientRect();
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        
        let adjustedX = x;
        let adjustedY = y;
        
        // Adjust if tooltip would go off right edge
        if (x + tooltipRect.width > viewportWidth) {
          adjustedX = e.clientX - tooltipRect.width - 15;
        }
        
        // Adjust if tooltip would go off bottom edge
        if (y + tooltipRect.height > viewportHeight) {
          adjustedY = e.clientY - tooltipRect.height - 15;
        }
        
        // Adjust if tooltip would go off top edge
        if (adjustedY < 10) {
          adjustedY = e.clientY + 15;
        }
        
        tooltip.style.left = adjustedX + 'px';
        tooltip.style.top = adjustedY + 'px';
        tooltip.style.opacity = 1;
      });

      section.addEventListener('mouseleave', () => {
        tooltip.style.opacity = 0;
      });
    });
  })();
</script>
```

```{seealso}
The **UN Global Assessment Report on Disaster Risk Reduction (GAR)** is the flagship report of the United Nations on worldwide efforts to reduce disaster risk. The GAR is published by the UN Office for Disaster Risk Reduction (UNDRR), and is the product of the contributions of nations, public and private disaster risk-related science and research, amongst others.

- **[UNDRR GAR 2022](https://www.undrr.org/global-assessment-report-disaster-risk-reduction-gar)**
```
