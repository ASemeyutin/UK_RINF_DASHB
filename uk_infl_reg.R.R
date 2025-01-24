# ============================================================================= #
#
library(tidyverse)
library(dplyr)
library(data.table)
library(readxl)
library(tidyr)
library(lubridate)
library(zoo)
library(shiny)
library(purrr)
#
directory = getwd()
rm(list = setdiff(ls(), c("directory", "temp_format")))
dta = fread(paste0(directory, "/FormattedData/CoicopWeightedtillLatestKCleaned.csv"))
#
dta = dta %>% subset(select = c(quote_date, item_id, region, shop_code, shop_type, price,stratum_type, item_weight))
dta[, productID := .GRP, by = .(item_id, region, shop_code, shop_type, stratum_type)]
dta = dta %>% subset(select = -c(shop_code, shop_type, stratum_type))
dta = arrange(dta, productID, quote_date)
#
dta_regions = list()
for (j in 2:13){
  dta_regions[[c(j-1)]] = dta[dta$region==j, -3]
}
#
#
#
for (k in 1:12){
  dta_regions[[k]][, l_price := shift(.SD$price, n = 1, type = "lag", fill = NA), by = productID]
  dta_regions[[k]]$pc = (dta_regions[[k]]$price / dta_regions[[k]]$l_price) - 1
  # 
  dta_regions[[k]] = dta_regions[[k]] %>% subset(!is.na(pc))
  dta_regions[[k]][, Date := as.Date(paste0(substring(quote_date,1,4), "-", 
                               substring(quote_date,5,6), "-01"))]
  dta_regions[[k]][, l_Date := shift(.SD$Date, n = 1, type = "lag", fill = NA), by = productID]
  
  dta_regions[[k]][, weeks_diff := as.numeric(difftime(Date, l_Date, units = "weeks"))]
  dta_regions[[k]] = dta_regions[[k]] %>% subset(weeks_diff < 5)
  dta_regions[[k]] = dta_regions[[k]] %>% subset(select = -c(weeks_diff, l_Date, Date))
  # 
  dta_regions[[k]][, qt_pc := quantile(pc, 0.975, na.rm = TRUE), by = quote_date]
  dta_regions[[k]][, qb_pc := quantile(pc, 0.025, na.rm = TRUE), by = quote_date]
  dta_regions[[k]] = dta_regions[[k]] %>% subset(pc > qb_pc & pc < qt_pc)
  dta_regions[[k]] = dta_regions[[k]] %>% subset(select = -c(qt_pc, qb_pc))
  # 
  dta_regions[[k]] = dta_regions[[k]][, .(pc = mean(pc), item_weight = mean(item_weight)), by = c("item_id", "quote_date")]
  dta_regions[[k]] = dta_regions[[k]][, .(w_m_pc = weighted.mean(pc, item_weight, na.rm=TRUE)), by = quote_date]
  #
  colnames(dta_regions[[k]]) = c("date", "infl")
  dta_regions[[k]]$Type = "Ours"
  #
  dta_regions[[k]] = arrange(dta_regions[[k]], date)
  dta_regions[[k]]$cpi = NA
  dta_regions[[k]]$cpi[1] = 1
  #
  for(i in 1:nrow(dta_regions[[k]])){
    if(i == 1){
      dta_regions[[k]]$cpi[i] = 1*(1+dta_regions[[k]]$infl[i])
    } else {
      dta_regions[[k]]$cpi[i] = dta_regions[[k]]$cpi[i-1] * (1 + dta_regions[[k]]$infl[i])
    }
  }
  #
  dta_regions[[k]][, l_cpi := shift(cpi, n = 12, type = "lag", fill = NA)]
  dta_regions[[k]]$infl = ((dta_regions[[k]]$cpi / dta_regions[[k]]$l_cpi) - 1)*100
  dta_regions[[k]] = as.data.table(dta_regions[[k]])[, date2 := as.Date(paste0(substring(date,1,4), "-", 
                                                                               substring(date,5,6), "-01"))]
  #
  dta_regions[[k]] = dta_regions[[k]] %>% subset(select = c(date, Type, infl))
  dta_regions[[k]] = dta_regions[[k]] %>% subset(!is.na(infl))
  #
}
#
UK_infl = fread(paste0(getwd(), "/UK_infl.csv"))
for (m in 1:12){
  dta_regions[[m]]$date2 = as.Date(paste0(substring(dta_regions[[m]]$date,1,4), "-", 
                                          substring(dta_regions[[m]]$date,5,6), "-01"))
  UK_infl = cbind(UK_infl, dta_regions[[m]]$infl)
  }
#
colnames(UK_infl)[5:16]=c("London_infl",
                          "SouthEast_infl",
                          "SoutWest_infl",
                          "EastAnglia_infl",
                          "EastMidlands_infl",
                          "WestMidlans_infl",
                          "YorkHumb_infl",
                          "NorthWest_infl",
                          "NorthEast_infl",
                          "Wales_infl",
                          "Scotland_infl",
                          "NI_infl")
#
write.csv(UK_infl, paste0(getwd(), "/UK_infl_reg.csv"), row.names = FALSE)
#
# UK Regions:
# 2(1) London
# 3(2) South East
# 4(3) South West
# 5(4) East Anglia
# 6(5) East Midlands
# 7(6) West Midlands
# 8(7) Yorkshire & the Humber
# 9(8) North West
# 10(9) North East
# 11(10) Wales
# 12(11) Scotland
# 13(12) Northern Ireland
# ============================================================================= #