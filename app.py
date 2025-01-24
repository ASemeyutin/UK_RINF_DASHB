# ============================================================================================================ #
#
import os
from uk_plots import *
from shinyswatch import theme
from shiny import App, render, ui
#
# =========================================================================================================== #
#
app_ui = ui.page_fillable(
        ui.tags.style(
        """
        .bottom-paragraph {
            position: fixed;
            bottom: 0;
            width: 95%;
            text-align: center;  
        }
        """
        ),
        ui.navset_tab(
                ui.nav_panel("UK Inflation by Region",  
                             ui.layout_column_wrap(
                             ui.div(p1,
                             ui.download_button("d_download", "Download Source Data")), 
                             ui.div(p2), 
                             ),),
                ui.nav_panel("Description", 
                             ui.markdown(
                                     """
                                     ### App version 0.0.1.
                                     
                                     Regional and Overall UK Micro CPI Inflation (12 month-on-month basis) was computed with the 
                                     [ONS Consumer Price Inflation Item Idices and Price Quotes](https://www.ons.gov.uk/economy/inflationandpriceindices/datasets/consumerpriceindicescpiandretailpricesindexrpiitemindicesandpricequotes) data using ONS own weighting.
                                     
                                     It is worth noting that Micro CPI data provided by the ONS does not cover certain items that could be of particular interest at the regional level, such as OOH (owner occupeirs' housing) component of the UK CPIH based inflation. 
                                     For full details please refer to the data technical manual and additional details on the [ONS website](https://ons.gov.uk/economy/inflationandpriceindices/methodologies/consumerpricesindicestechnicalmanual2019).
                                     
                                     Regional Micro CPI inflation was computed by accordingly modifying **R code** of [Kristian Gado and Raphael Schoenie](https://www.ukmicrocpi.com/home). 
                                     I also would like to encourage reading their article on the [BOE's Bank Underground](https://bankunderground.co.uk/2024/01/17/beyond-the-average-patterns-in-uk-price-data-at-the-micro-level/) page.
                                     It is very insightful and let me discover [this](https://www.ft.com/content/a5eb83c0-92f1-42a5-bea0-ac8d20d039a3) amazing inflation related meme by the FT.
                                                                          
                                     All errors (if any) are my own. Artur Semeyutin.
                                     """
                             )),
        ),        
        ui.p("App version 0.0.1.", class_="bottom-paragraph"),
        theme=theme.lux,
)
#
def server (input, output, session):
        @output
        @render.plot(width=400, height=800)
        def UK_INFL_MAP():
                return plot1(my_input_1 = input.date_map(), my_input_2 = input.map_bench())
        #
        @render.plot(width= 700)
        def UK_TS():
                return plot2(my_input_3 = input.opt_1(), my_input_4 = input.opt_2(), my_input_5= input.date_range())
        @render.download()
        def d_download():
                my_data = os.path.join(os.path.dirname(__file__), "UK_infl_reg.csv")
                return my_data 
#
app = App(app_ui, server)
# ============================================================================================================ #