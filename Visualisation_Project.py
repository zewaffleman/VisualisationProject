# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 18:01:52 2019

@author: Vik
"""
import pandas as pd
import matplotlib as plt
import matplotlib.cm as cm
import numpy as np

from math import pi

from bokeh.io import show, output_file, curdoc
from bokeh.models import LinearColorMapper, BasicTicker,  ColorBar , ColumnDataSource, HoverTool, CustomJS, Range1d, LinearAxis, TapTool
from bokeh.plotting import figure
from bokeh.themes import built_in_themes
from bokeh.layouts import gridplot, layout
from bokeh.palettes import Viridis3

output_file("Bokeh.html")

df = pd.read_csv('grimdatagovau.csv', encoding='cp1252')
dfPop = pd.read_csv('popularityOfSmoking.csv', encoding='cp1252')

# just select lung cancer
#this fucks it up fix this :)
df = df[df.cause_of_death == 'Lung cancer (ICD-10 C33, C34)']

# drop "Person" data
df = df.query('SEX != "Persons"')
df = df.query('SEX != "Females"')

#drop the kids from it
df = df.query('AGE_GROUP != "5–9"')
df = df.query('AGE_GROUP != "0–4"')


# drop everything before 1910
df = df.query('YEAR >= 1945')

TOOLS = "save,box_zoom,reset"

yearMin = min(df.YEAR)
yearMax = max(df.YEAR)

source = ColumnDataSource(data={
        'AGE_GROUP' : df.AGE_GROUP,
        'YEAR' : df.YEAR, 
        'DEATHS' : df.deaths, 
        'RATE' : df.rate, 
        })

#converting matplotlib colour map to fkin bokeh ones >:(
colormap =cm.get_cmap("gist_heat_r") #choose any matplotlib colormap here
bokehpalette = [plt.colors.rgb2hex(m) for m in colormap(np.arange(colormap.N))]

mapper = LinearColorMapper(palette = bokehpalette, low=min(df.deaths), high=1100)
          
age_group = list(df.AGE_GROUP)

p1 = figure(title="Deaths caused by lung cancer in Australia from ({0} - {1})".format(yearMin, yearMax),
           x_range=[yearMin, yearMax], 
           y_range=[age_group[0], age_group[1], age_group[2], age_group[3], age_group[4], age_group[5], age_group[6], age_group[7], age_group[8], 
                    age_group[9], age_group[10], age_group[11], age_group[12], age_group[13], age_group[14], age_group[15]], 
                    plot_width = 800, 
                    plot_height = 350, 
                    tools = TOOLS, toolbar_location=None)

p1.grid.grid_line_color = None
p1.axis.axis_line_color = None
p1.axis.major_tick_line_color = None
p1.xaxis.axis_label = 'Year'
p1.yaxis.axis_label = 'Age Group'
p1.axis.major_label_text_font_size = "8pt"
p1.axis.major_label_standoff = 0
p1.xaxis.major_label_orientation = pi / 3

rc = p1.rect(x="YEAR", y="AGE_GROUP", width=1, height=1,
       source=source, 
       fill_color={'field': 'DEATHS', 'transform': mapper},
       line_color='white')

color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="8pt",
                     ticker=BasicTicker(desired_num_ticks=len('Magma256')),
                     label_standoff=6, border_line_color=None, location=(0, 0))

p1.add_layout(color_bar, 'right')

#hover tool for additional plots
p2 = figure(plot_width = 800, plot_height = 350, title = "Deaths caused by lung cancer for specified age group", toolbar_location=None)

p2.extra_y_ranges = {"percent": Range1d(start=0, end=100)}

sourceLine = ColumnDataSource(data = {'x': [], 'y': []})

lnData = p2.line(x = 'x', y = 'y', line_width = 2, source = sourceLine)
lnPop = p2.line(x = dfPop.Year, y = dfPop.Total, line_width = 2, y_range_name = "percent")


callbackLine = CustomJS(args={'rect': rc.data_source.data, 'line': lnData.data_source}, code="""
                    
var rdataYear = rect.YEAR;
var rdataAgeGroup = rect.AGE_GROUP;
var rdataDeaths = rect.DEATHS;

var data = {'x': [], 'y': [], 'x1': [], 'y1': []};
var deaths = [];

var years = [1945,1946,1947,1948,1949,1950,1951,1952,1953,1954,1955,1956,1957,1958,1959,1960,1961,1962,1963,1964,1965,1966,1967,1968,1969,1970,1971,1972,1973,1974,1975,1976,1977,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017
]

var indices = cb_data.index.indices;

var newarr = rect.AGE_GROUP.map((e,i) => e === rdataAgeGroup[indices] ? i : undefined).filter(x => x);

for (var i = 0; i < newarr.length; i++){     
    deaths.push(rdataDeaths[newarr[i]])
}

line.data = {x: years, y: deaths}

""")

p2.x_range=Range1d(1945, 2017)
p2.y_range=Range1d(0,1100)
p2.grid.grid_line_color = None
p2.axis.axis_line_color = None
p2.axis.major_tick_line_color = None
p2.xaxis.axis_label = 'Year'
p2.yaxis.axis_label = 'Deaths'
p2.axis.major_label_text_font_size = "8pt"
p2.axis.major_label_standoff = 0
p2.xaxis.major_label_orientation = pi / 3

p2.add_layout(LinearAxis(y_range_name="percent", axis_label='Smoking Pervalence in Australia (%)'), 'right')

sourceHist = ColumnDataSource(data = {'x': [], 'y': []})

p3 = figure(plot_width = 450, plot_height = 350, x_range=df.groupby('AGE_GROUP'), title="Distribution of deaths for specified Year", toolbar_location=None)

hist = p3.vbar(x = 'x', top = 'y', width = 0.9, source = sourceHist)

callbackHist = CustomJS(args={'rect': rc.data_source.data, 'vbar': hist.data_source}, code="""
var rdataYear = rect.YEAR;
var rdataAgeGroup = rect.AGE_GROUP;
var rdataDeaths = rect.DEATHS;

var deathsYear = [];

var ageGroup = ['10–14','15–19','20–24','25–29','30–34','35–39','40–44','45–49','50–54','55–59','60–64','65–69','70–74','75–79','80–84','85+']

var indices = cb_data.index.indices;

var newarr = rect.YEAR.map((e,i) => e === rdataYear[indices] ? i : undefined).filter(x => x);

for (var i = 0; i < newarr.length-2; i++){     
    deathsYear.push(rdataDeaths[newarr[i]])
}

vbar.data = {x: ageGroup, y: deathsYear}
""")

p3.y_range=Range1d(0,1100)
p3.grid.grid_line_color = None
p3.axis.axis_line_color = None
p3.axis.major_tick_line_color = None
p3.xaxis.axis_label = 'Age groups'
p3.yaxis.axis_label = 'Deaths'
p3.axis.major_label_text_font_size = "8pt"
p3.axis.major_label_standoff = 0
p3.xaxis.major_label_orientation = pi / 3

p1.add_tools(HoverTool(tooltips=[('Year', '@YEAR'), ('Age Group', '@AGE_GROUP'),('Deaths', '@DEATHS'),('Rate', '@RATE')], callback=callbackLine))
p1.add_tools(HoverTool(tooltips = [], callback = callbackHist))


l = layout([
        [p1], 
        [p2, p3]
        ] ,sizing_mode='stretch_both')

curdoc().theme = 'dark_minimal'
show(l)      # show the plot
