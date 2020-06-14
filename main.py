# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from bokeh.io import curdoc
from bokeh.layouts import column, layout
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput, MultiSelect,RangeSlider, PointDrawTool
from bokeh.plotting import figure, output_file, show
import bokeh.palettes as pl


df_all = pd.read_csv(r'./test/data/lidata.CSV', header = 0)


df_all['ULR'] = df_all['UL'] / df_all['EP']
unique_company = ["All"] + df_all['公司'].unique().tolist()
unique_business = ["All"] + df_all['险种'].unique().tolist() 
unique_product = ["All"] + df_all['险别'].unique().tolist() 
#combinations = len(unique_company) * len(unique_business) * len(unique_product)
#print(combinations)
color = pl.mpl['Plasma'][len(unique_product)]

df_all["color"] = [color[unique_product.index(pro)] for pro in df_all["险别"].values]

year_start = df_all['事故年'].min()
year_end =  df_all['事故年'].max()

# 这里可以改变选项是什么
axis_map = {
    "ULR": "ULR",
    "ULAE": "EP",
    "DAC":'DAC'
}


year_range = RangeSlider(start=year_start, end=year_end, value=(year_start,year_end), step=1,
                       title="展示年")
Slider(title="开始展示年", start=year_start, end=year_end, value=year_start, step=1)
max_year = Slider(title="结束展示年", start=year_start, end=year_end, value=year_end, step=1)
company = Select(title="公司选择", value="All",
               options=unique_company)
business = Select(title="险别选择", value="All",
               options=unique_business)
product = Select(title="险种选择", value="All",
               options=unique_product)
#product = MultiSelect(title="险种选择", value=["All"],
#                           options=unique_product)
#director = TextInput(title="Director name contains")
#cast = TextInput(title="Cast names contains")
#x_axis = Select(title="X Axis", options=sorted(axis_map.keys()), value="Data 1 by lmk")
y_axis = Select(title="展示值", options=sorted(axis_map.keys()), value="ULR")

TOOLTIPS=[
    ("公司为", "@com"),
    ("年:", "@year"),
    ("险别为", "@business"),
    ("险种为", "@pro")
]
TOOLS="pan,wheel_zoom,box_select,lasso_select,reset"
p = figure(tools=TOOLS,plot_height=100, plot_width=200, title="", toolbar_location="above", tooltips=TOOLTIPS, sizing_mode="scale_both")

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(x=[], y=[],color=[],com=[], year=[], business=[], pro=[], alpha=[]))


r = p.circle(x="x",y="y" ,source=source, size=10, color = 'color', alpha=0.6, hover_color='white', hover_alpha=0.5)#, color="color", line_color=None, line_alpha="alpha"

draw_tool = PointDrawTool(renderers=[r], empty_value='black')
p.add_tools(draw_tool)
p.toolbar.active_tap = draw_tool

def select_products():
    company_val = company.value.strip()
    business_val = business.value.strip()
    product_val = product.value.strip()
    #product_val = [pro.strip() for pro in product.value]
    selected = df_all[
        (df_all.事故年 >= year_range.value[0]) &
        (df_all.事故年 <= year_range.value[1]) 
    ]
    if (company_val != "All"):
        selected = selected[selected.公司.str.contains(company_val)==True]
    if (business_val != "All"):
        selected = selected[selected.险种.str.contains(business_val)==True]
    if (product_val != "All"):
        selected = selected[selected.险别.str.contains(product_val)==True]
    return selected

def update():
    df = select_products()
    x_name = "事故年"
    y_name = axis_map[y_axis.value]

    #p.xaxis.axis_label = df["Year"]
    #p.yaxis.axis_label = y_axis.value
    p.title.text = "%d points selected" % len(df)
    source.data = dict(
        x=df[x_name],
        y=df[y_name],  #,
        com=df["公司"].values,
        year=df["事故年"].values,
        business=df["险别"].values,
        pro=df["险种"].values,
        color = df["color"]
        #alpha=df["alpha"],
    )
controls = [company, business, product, year_range,  y_axis]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

inputs = column(*controls, width=320, height=1000)
inputs.sizing_mode = "fixed"
l = layout([
   # [desc],
    [inputs, p],
], sizing_mode="scale_both")

update()

curdoc().add_root(l, p)
