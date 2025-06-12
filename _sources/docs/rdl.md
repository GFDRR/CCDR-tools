# Risk Data Library

The [**Risk Data Library**](https://riskdatalibrary.org) project led by GFDRR grew out of in-depth Disaster Risk Management community consultation on improving access to risk information.
Its overarching purpose is to support disaster resilience work by making risk data easier and more effective to work with.

Building on GFDRR experience, extensive & intensive review of risk literature and case studies, and partnership with some of the main risk data actors ([GEM, UCL EPICentre, BGS, OasisHUB and more](https://riskdatalibrary.org/project)), the RDL proposes a standard data and metadata schema to organise, format, describe, store and share risk data.
<br><br>
More information are available in the [**RDL documentation**](https://rdl-standard.readthedocs.io/en/docs.mat/).

The [**Risk Data Library Collection**](https://datacatalog.worldbank.org/search/collections/rdl) is a catalogue where **Risk Datasets** produced or used by World Bank analytics are stored and organised by the [**RDL standard metadata schema**](https://docs.riskdatalibrary.org/en/latest/reference/browser/).


<!--
  <style>
    body {
      background: #111;
      color: white;
      font-family: sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      margin: 0;
      padding: 20px;
      box-sizing: border-box;
    }

    .container {
      position: relative;
      width: 90vw;
      max-width: 600px;
      height: 90vh;
      max-height: 600px;
      display: flex;
      justify-content: center;
      align-items: center;
    }

    svg {
      width: 100%;
      height: 100%;
      max-width: 100%;
      max-height: 100%;
    }

    .section {
      transition: transform 0.4s ease, filter 0.3s ease, z-index 0.1s ease;
      cursor: pointer;
      transform-origin: center;
      z-index: 1;
    }

    .section:hover {
      transform: scale(1.08);
      filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.8));
      z-index: 10;
    }

    .section-text {
      pointer-events: none;
      font-family: Arial, sans-serif;
      font-weight: bold;
      font-size: 110px;
      text-anchor: middle;
      dominant-baseline: central;
      transition: font-size 0.4s ease;
    }

    .tooltip {
      position: fixed;
      background: rgba(0,0,0,0.9);
      color: white;
      padding: 8px 12px;
      border-radius: 6px;
      pointer-events: none;
      opacity: 0;
      transition: opacity 0.2s;
      white-space: nowrap;
      z-index: 1000;
      font-size: 14px;
      border: 1px solid rgba(255,255,255,0.2);
    }
  </style>

<div class="container">
  <div class="tooltip" id="tooltip"></div>
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" preserveAspectRatio="xMidYMid meet">

    <!-- Hazard (Blue) -->
    <g class="section" data-info="Hazard: Potentially damaging physical event">
      <path d="M505.5 942.9 c-59.7 -3.6 -114 -47.1 -156 -125 -5.9 -10.9 -21.5 -43.8 -21.5 -45.4 0 -0.3 -0.9 -2.4 -1.9 -4.8 -2.9 -6.4 -12.5 -35.6 -16.5 -50.3 -7 -25.4 -13.4 -59.9 -16 -86.4 -1.7 -16.5 -4 -56.9 -3.3 -57.7 0.3 -0.2 3.1 1.1 6.3 2.9 9.8 5.5 35.6 17.4 50.1 23.2 58.7 23.1 126.4 34.1 188.4 30.7 21.4 -1.2 46 -3.9 60.9 -6.6 23.5 -4.4 62.3 -15.9 84.3 -24.9 14.5 -5.9 39.7 -17.5 48.2 -22.1 l8 -4.4 -0.3 13.2 c-2.2 109.2 -38.2 217.5 -96.7 290.2 -23.5 29.3 -55.7 53.2 -83.4 61.9 -15.7 4.9 -31.3 6.6 -50.6 5.5z" fill="#007fc3" />
      <text x="510" y="750" class="section-text" fill="white">H</text>
    </g>
    
    <!-- Exposure (Teal) -->
    <g class="section" data-info="Exposure: Degree to which assets are at risk">
      <path d="M259.5 534.2 c-31.3 -21.1 -55 -40.7 -82.6 -68.2 -28.2 -28.1 -44.1 -47.4 -63.2 -76.6 -15.2 -23.2 -24.3 -40 -33.1 -61 -2.6 -6 -5.1 -11.8 -5.5 -12.9 -0.5 -1.1 -2.1 -5.6 -3.6 -10 -23.1 -69.5 -11 -132.6 32.5 -169 23.2 -19.3 54.5 -32.8 91.5 -39.2 14.2 -2.5 59.8 -2.5 77.5 0 27 3.7 62 11.2 81.2 17.3 11 3.5 41 14.5 49 18 30.9 13.5 63.3 31.6 87.1 48.6 l4.7 3.5 -10.2 7.9 c-43.8 33.7 -83.7 73.5 -113.3 112.9 -27.7 36.9 -45.1 66.5 -60.2 102.5 -19 45.1 -29.4 81.9 -36.8 130.8 -0.4 2.3 -1 4.2 -1.3 4.2 -0.4 0 -6.5 -4 -13.7 -8.8z" fill="#00cbab" />
      <text x="235" y="260" class="section-text" fill="white">E</text>
    </g>
    
    <!-- Risk (Red) -->
    <g class="section" data-info="Impact: Consequences of hazard affecting exposed and vulnerable assets">
      <path d="M489 612.9 c-51.8 -2.4 -111.5 -17.7 -162 -41.5 -25.8 -12.2 -37 -18.5 -37 -20.8 0 -4.1 4.1 -28.3 7.1 -42.6 3.5 -16.3 12 -46.5 17.3 -61.3 17.4 -48.2 39.3 -88.6 71 -131 26.9 -36 71.4 -79.7 114.7 -112.8 l11.7 -8.8 5.5 3.9 c33.1 23.1 77.5 63.5 103.4 94 9.8 11.6 27.8 35.3 36 47.5 39 58.1 66.6 129.3 75.7 195.5 0.9 6.3 1.8 12.7 2.1 14.2 0.4 2.6 -0.2 3.2 -7.3 7.3 -33.6 19.9 -89.5 40.8 -131.7 49.4 -13 2.6 -42.5 5.9 -59 6.6 -27.4 1.1 -31.5 1.2 -47.5 0.4z" fill="#f3436a" />
      <text x="510" y="420" class="section-text" fill="white">R</text>
    </g>
    
    <!-- Vulnerability (Yellow) -->
    <g class="section" data-info="Vulnerability: Susceptibility of exposed elements to damage">
      <path d="M750.5 538.7 c-8.3 -55.4 -23 -103.3 -46.4 -152.2 -12.3 -25.7 -28.8 -52.3 -49.6 -79.8 -16 -21.3 -25.1 -32.1 -42.6 -50.1 -25.5 -26.3 -54.3 -51.7 -77.7 -68.3 l-4.3 -3.1 4.3 -3.4 c22.2 -17.7 67.1 -42.5 101.8 -56.1 68.6 -27.1 144.4 -37.2 198.2 -26.6 26.4 5.2 54 16.3 74.2 29.6 15.5 10.3 31.8 28.8 40.3 45.7 23.8 47.3 18.7 105.9 -15.3 173.8 -21.8 43.6 -48 79.4 -86.4 117.9 -27.8 28 -59.4 53.6 -90.2 73.2 l-5.6 3.6 -0.7 -4.2z" fill="#ffc757" />
      <text x="780" y="260" class="section-text" fill="white">V</text>
    </g>
  </svg>
</div>

<script>
  const tooltip = document.getElementById('tooltip');
  const sections = document.querySelectorAll('.section');

  sections.forEach(section => {
    section.addEventListener('mousemove', e => {
      tooltip.textContent = section.dataset.info;
      
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
      
      tooltip.style.left = adjustedX + 'px';
      tooltip.style.top = adjustedY + 'px';
      tooltip.style.opacity = 1;
    });

    section.addEventListener('mouseleave', () => {
      tooltip.style.opacity = 0;
    });
  });
</script>

-->
