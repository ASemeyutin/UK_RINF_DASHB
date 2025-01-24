# UK Regional Inflation Dashboard (Shiny App) Jan 1997 - Dec 2024

This repo replicates a Shiny App for the UK Inflation Dashboard (12 month-on-month basis) for every region in the UK. The dashboard can be accessed [here](link_placeholder). Currently it allows exploring monthly inflation by region, perfrorm comparisons with the national average and/or at the region-to-region level(s) over time through several interactive visualisations. 

Inflation is computed with the [ONS Micro CPI Prices and Quotes Database](https://www.ons.gov.uk/economy/inflationandpriceindices/datasets/consumerpriceindicescpiandretailpricesindexrpiitemindicesandpricequotes) by following the approach of [Kristian Gado and Raphael Schoenie](https://www.ukmicrocpi.com/home) and decomposing their Micro CPI based inflation to the regional level. 
```
Regional inflation computations can be replicated with uk_infl_reg.R file.
```
*Please note that to replicate regional inflation, it is important to obtain raw files from the ONS first and then follow Gado and Schoenie guidlines on how to merge and clean ONS raw files (run their R scripts). Unfrotunately, their source code is only available through their website (link above) and I could not contribute(?) to it directly here on github.*

# App Demo (Output)

![](https://github.com/ASemeyutin/UK_RINF_DASHB/blob/main/app_demo.gif)
