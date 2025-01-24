# ============================================================================================================ #
#
from pathlib import Path  
from datetime import date
import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from drawarrow import fig_arrow
from pyfonts import load_font
from highlight_text import fig_text, ax_text
from datetime import datetime
from shiny import ui
#
UK_infl = Path(__file__).parent / "UK_infl_reg.csv"
fname_geo_bndr = Path(__file__).parent / "NUTS1_Jan_2018_UGCB_in_the_UK_2022.geojson"
font = load_font('https://github.com/dharmatype/Bebas-Neue/blob/master/fonts/BebasNeue(2018)ByDhamraType/ttf/BebasNeue-Regular.ttf?raw=true')
other_font = load_font('https://github.com/bBoxType/FiraSans/blob/master/Fira_Sans_4_3/Fonts/Fira_Sans_TTF_4301/Normal/Roman/FiraSans-Light.ttf?raw=true')
other_bold_font = load_font('https://github.com/bBoxType/FiraSans/blob/master/Fira_Sans_4_3/Fonts/Fira_Sans_TTF_4301/Normal/Roman/FiraSans-Medium.ttf?raw=true')
#
color_1 = '#335c67'
color_2 = '#9e2a2b'
background_color = 'white'
text_color = 'black'
#
# ============================================================================================================ #
#
INF = pd.read_csv(UK_infl)
INF["date2"] = pd.to_datetime(INF["date2"])
#
# =========================================================================================================== #
#
p1 = ui.card(
        ui.card_header("Inflation Map"),
        ui.input_date("date_map", "Select Date", 
                      format = "mm/yyyy", 
                      value = "2024-12-31", 
                      min = "1997-04-01", 
                      max = "2024-12-31",
                      startview="decade"),
        # ui.input_select("map_date", "Select Date (YYYYMM)", choices=INF["date"].tolist()[::-1]),
        ui.input_select("map_bench", "Select Benchmark", choices=["UK ONS CPIH Inflation", "UK Micro CPI Inflation"]),
        ui.output_plot("UK_INFL_MAP"),
        height = "1055px"
)
#
p2 = ui.card(
        ui.card_header("Inflation Over Time"),
        ui.input_select("opt_1", "Select Inflation for:", choices = INF.columns.tolist()[3:16]),
        ui.input_select("opt_2", "Select Inflation for:", choices = INF.columns.tolist()[2:16]),
        ui.output_plot("UK_TS"),
        ui.input_date_range("date_range", "Select Date Range",
                            format = "dd/mm/yyyy",
                            start = "1997-04-01",
                            end = "2024-12-31",
                            min = "1997-04-01",
                            max = "2024-12-31",
                            startview="decade"),
        # ui.input_slider("d_slide", "Date Range", min=0, max=330, value = [0,330]),
        height = "1055px"
)
#
def plot1(my_input_1, my_input_2, figsize=(8, 6), dpi=900):
        #
        # U_choice_date=INF.index[INF["date"]==int(my_input_1)][0]
        U_choice_date=INF.index[INF["date"]==int(my_input_1.strftime("%Y%m"))][0]
        U_choice_infl = my_input_2
        #
        if U_choice_infl == "UK ONS CPIH Inflation":
                U_choice_infl_benchmark = "infld1"
                k=2 
        else:
                U_choice_infl_benchmark = "infld2"
                k=3
        #
        INFym = INF.iloc[U_choice_date,2:]
        INFym = pd.DataFrame({
                "region" : ["London", "South East", "South West", "East of England", 
                                "East Midlands", "West Midlands", "Yorkshire and Humber", " North West", 
                                "North East", "Wales", "Scotland", "Northern Ireland"],
                "infl" : INFym.iloc[2:].values,
                "infld1" : INFym.iloc[0] - INFym.iloc[2:].values,
                "infld2" : INFym.iloc[1] - INFym.iloc[2:].values
        })
        geodf = gpd.read_file(fname_geo_bndr)
        INForder = [6, 7, 8, 5, 3, 4, 2, 1, 0, 9, 10, 11]
        geodf = geodf.loc[INForder].reset_index(drop=True)
        geodf = geodf.rename({"nuts118nm": "region"}, axis =1)
        geodf["region"] = INFym["region"]
        #
        INFym_geo = geodf.merge(INFym, on = 'region').set_index('region')
        INFym_geo = INFym_geo.rename({"nuts118cd" : "reg"}, axis =1)
        INFym_geo["reg"] = ["LDN", "SE", "SW", "EE", "EM", "WM", "YH", "NW", "NE", "WLS", "SCT", "NI"]
        #
        data_projected = INFym_geo.to_crs(epsg=3035)
        data_projected['centroid'] = data_projected.geometry.centroid
        INFym_geo['centroid'] = data_projected['centroid'].to_crs(INFym_geo.crs)
        #
        my_colors = [color_1, color_2]
        my_color_map = np.where(INFym_geo[U_choice_infl_benchmark]>0, my_colors[0], my_colors[1])
        #
        regions_to_ann = ["SE", "SW", "EE", "EM", "WM", "YH", "WLS", "SCT", "NI"]
        adjustments = {
                "SE"  : (0, -0.2),
                "WLS" : (-0.1, -0.35),
                "SCT": (0.2, 0),
                "WM": (0.05, -0.05)
        }
        arrow_props = dict(width=0.8, head_width=3, head_length=6, color=text_color)

        fig, ax = plt.subplots()
        fig.set_facecolor(background_color)
        ax.set_ylim(49, 58.725)
        ax.set_xlim(-8.5, 1.9)
        ax.set_axis_off()
        # Legend
        labels = [f"< {INF.iloc[U_choice_date, k]:.2f}" , f"> {INF.iloc[U_choice_date, k]:.2f}"]
        # 
        rectangle_width = 1
        rectangle_height = 0.5
        legend_x = -1.55
        legend_y_start = 57.75
        legend_y_step = 0.575
        #
        for i in range(len(labels)):
                ax.add_patch(plt.Rectangle((legend_x, legend_y_start - i * legend_y_step), rectangle_width, rectangle_height,
                                color=my_colors[i], ec = text_color, lw=0.5))
                ax.text(legend_x + 1.25, legend_y_start - i * legend_y_step + 0.25, labels[i], 
                        fontsize= 10, fontproperties=other_font, color=text_color, va='center')

        INFym_geo.plot(column = "infl", ax = ax, color=my_color_map, edgecolor=text_color, linewidth=0.5)
        #
        for reg in regions_to_ann:
                centr = INFym_geo.loc[INFym_geo["reg"] == reg, "centroid"].values[0]
                x, y = centr.coords[0]
                rate = INFym_geo.loc[INFym_geo['reg'] == reg, 'infl'].values[0]
                try:
                        x += adjustments[reg][0]
                        y += adjustments[reg][1]
                except KeyError:
                        pass
                ax_text(x=x, y=y, s=f"<{reg.upper()}>: {rate:.2f}", fontsize= 9, font=other_font, color=text_color,
                        ha='center', va='center', ax=ax, highlight_textprops=[{'font': other_bold_font}])
        #
        fig_arrow(tail_position=(0.2, 0.33), head_position=(0.785, 0.3125), radius=0.15, **arrow_props) # LND
        fig_arrow(tail_position=(0.75, 0.7), head_position=(0.625, 0.58), radius=-0.3, **arrow_props) # NE
        fig_arrow(tail_position=(0.35, 0.49), head_position=(0.57, 0.54), radius=-0.3, **arrow_props) # NW
        #
        LDN = INFym_geo.loc[INFym_geo['reg'] == 'LDN', 'infl'].values[0]
        NE = INFym_geo.loc[INFym_geo['reg'] == 'NE', 'infl'].values[0]
        NW = INFym_geo.loc[INFym_geo['reg'] == 'NW', 'infl'].values[0]
        fig_text(s=f"<LDN>: {LDN:.2f}", x=0.2, y=0.34, highlight_textprops=[{'font': other_bold_font}],
                color=text_color, fontsize=9, font=other_font, ha='center', va='center', fig=fig)
        fig_text(s=f"<NE>: {NE:.2f}", x=0.75, y=0.71, highlight_textprops=[{'font': other_bold_font}],
                color=text_color, fontsize=9, font=other_font, ha='center', va='center', fig=fig)
        fig_text(s=f"<NW>: {NW:.2f}", x=0.34, y=0.48, highlight_textprops=[{'font': other_bold_font}],
                color=text_color, fontsize=9, font=other_font, ha='center', va='center', fig=fig)
        return fig
        #
def plot2(my_input_3, my_input_4, my_input_5):
        opt_1 = my_input_3
        opt_2 = my_input_4
        #
        s_p=INF.index[INF["date"]==int(my_input_5[0].strftime("%Y%m"))][0]
        e_p=INF.index[INF["date"]==int(my_input_5[1].strftime("%Y%m"))][0]
        date_r = range(s_p, e_p)
        #
        INF_l =INF[["date2", opt_1, opt_2]]
        INF_l.loc[date_r,["diff"]] = INF_l[opt_1]-INF_l[opt_2] # had to use this syntax; pandas was throwing a warning ...

        my_dpi=96
        fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(920/my_dpi, 920/my_dpi), dpi=my_dpi)
        fig1.subplots_adjust(hspace=0.5)
        for column in INF.drop(['date','date2'], axis=1):
                ax1.plot(INF.loc[date_r, ['date2']], INF.loc[date_r, column], marker='', color='grey', linewidth=1, alpha=0.1)
        
        ax1.plot(INF_l.loc[date_r,'date2'], INF_l.loc[date_r, opt_1], marker='', color=color_1, linewidth=2, alpha=0.75)
        ax1.plot(INF_l.loc[date_r,'date2'], INF_l.loc[date_r, opt_2], marker='', color=color_2, linewidth=2, alpha=0.75)
        ax1.spines['bottom'].set_visible(True)  
        ax1.spines['top'].set_visible(False)     
        ax1.spines['right'].set_visible(False)   
        #
        for tick in ax1.get_xticklabels():
                tick.set_fontproperties(other_font)

        y1_ticks = ax1.get_yticks()
        ax1.set_ylim(y1_ticks[0], y1_ticks[-1])

        for tick in ax1.get_yticklabels():
                tick.set_fontproperties(other_font)

        ax2.plot(INF_l["date2"], INF_l["diff"], color="grey", linewidth=0.01, alpha=0.01)
        ax2.fill_between(INF_l["date2"], INF_l["diff"], where = (INF_l["diff"]>=0), color=color_1, alpha=0.75)
        ax2.fill_between(INF_l["date2"], INF_l["diff"], where = (INF_l["diff"]<0), color=color_2, alpha=0.75)
        ax2.spines['bottom'].set_visible(True)  
        ax2.spines['top'].set_visible(False)     
        ax2.spines['right'].set_visible(False)   
        
        for tick in ax2.get_xticklabels():
                tick.set_fontproperties(other_font)

        y2_ticks = ax2.get_yticks()
        ax2.set_ylim(y2_ticks[0], y2_ticks[-1])

        for tick in ax2.get_yticklabels():
                tick.set_fontproperties(other_font)
        
        fig_text(
                s=f"<{opt_1}> & <{opt_2}> Inflation Over Time", x=0.5, y=0.935,
                color=text_color, fontsize=12, font=other_font, ha='center', va='top', ax=ax1,
                highlight_textprops=[{'font': other_bold_font,
                                      'color': color_1}, {'font': other_bold_font,
                                                          'color': color_2}]
        )
        # 
        fig_text(
                s=f"<{opt_1}> & <{opt_2}> Inflation Difference Over Time", x=0.5, y=0.465,
                color=text_color, fontsize=12, font=other_font, ha='center', va='top', ax=ax2,
                highlight_textprops=[{'font': other_bold_font,
                                      'color': color_1}, {'font': other_bold_font,
                                                          'color': color_2}]
        )     
        return fig1
#
# ============================================================================================================ #