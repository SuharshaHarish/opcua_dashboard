from django.db.models.base import Model
from numpy.core.fromnumeric import sort
from opcua_app.models import Temperature
from django.shortcuts import render
import time,json
import websocket
import requests
import numpy as np, scipy.stats as st
import pandas as pd
from statistics import stdev,mean
from .models import Anomaly, Temperature,Pressure
from bokeh.plotting import figure
from bokeh.palettes import Category10, Plasma, Viridis
from bokeh.transform import cumsum
from bokeh.embed import components
from bokeh.models import HoverTool, LassoSelectTool, WheelZoomTool, PointDrawTool, ColumnDataSource, ImageURL
from bokeh.models.tickers import FixedTicker
from bokeh.models import DatetimeTickFormatter,NumeralTickFormatter

def home(request):

    return render(request,'opcua_app/home.html')

def anomaly_view(request):

    data = find_limits()

    #Retrieve the last five values of temp and pressure anomalies
    temp_anomalies = Anomaly.objects.filter(param_type='t').order_by('-id')[:5]
    pres_anomalies = Anomaly.objects.filter(param_type='p').order_by('-id')[:5]
    
    # anomalies = temp_anomalies | pres_anomalies
    # print(temp_anomalies[0])
    args = {
        'temp_anomalies':temp_anomalies,
        'pres_anomalies' : pres_anomalies,
        'pres_intrvl': data['pres_intrvl'],
        'temp_intrvl':data['temp_intrvl']

    }
    # print(data)
    return render(request,'opcua_app/anomaly.html',args)


def find_limits():

    #find temp mean confidence interval
    temps = Temperature.objects.all()
    temp_data = []
    for temp in temps:
        temp_value = temp.temp_value
        temp_data.append(temp_value)
    temp_intrvl = st.t.interval(0.95, len(temp_data)-1, loc=np.mean(temp_data), scale=st.sem(temp_data))
    
    #find pressure mean confidence interval
    press = Pressure.objects.all()
    pres_data = []
    for pres in press:
        pres_value = pres.pres_value
        pres_data.append(pres_value)
    pres_intrvl = st.t.interval(0.95, len(pres_data)-1, loc=np.mean(pres_data), scale=st.sem(pres_data))

    #calculate the upper and lower bounds
    temp_lower = round(temp_intrvl[0])
    temp_upper = round(temp_intrvl[1])
    pres_lower = round(pres_intrvl[0])
    pres_upper = round(pres_intrvl[1])
    temp_margin = round(stdev(temp_data))
    pres_margin = round(stdev(pres_data))

    args = {
        'pres_intrvl': (pres_lower-pres_margin,pres_upper+pres_margin),
        'temp_intrvl':(temp_lower-temp_margin,temp_upper+temp_margin)
    }
    
    #save pressure anomaly
    for pres in press:
        
        pres_value = pres.pres_value
        if pres_value in range(pres_lower-pres_margin,pres_upper+pres_margin):    
            pass        
        else:
            if not Anomaly.objects.filter(pres_key=pres).exists():

                pres_anomaly = Anomaly.objects.create(param_type="p", pres_key=pres)
                pres_anomaly.save()

    #save temp anomaly
    for temp in temps:

        temp_value = temp.temp_value
        if temp_value in range(temp_lower-temp_margin,temp_upper+temp_margin):
            pass
        else:
            if not Anomaly.objects.filter(temp_key=temp).exists():

                temp_anomaly = Anomaly.objects.create(param_type="t", temp_key=temp)
                temp_anomaly.save()
    return args
def graphs(request):

    #Create pressure graph

    press = Pressure.objects.all()
    pres_data,pres_timestamp = [],[]
    for pres in press:
        pres_value = pres.pres_value
        pres_timestamp.append(pres.timestamp)
        pres_data.append(pres_value)

    pres_timestamp_data = pd.to_datetime(pres_timestamp)
    title = "Pressure"
    source = ColumnDataSource(data=dict(pres_data = pres_data, pres_timestamp_data = pres_timestamp_data ))

    plot_case = figure(title= title , 
        x_axis_label= 'Time', 
        x_axis_type = 'datetime',
        y_axis_label= 'Pressure (Pa)',
        tools="pan,wheel_zoom,reset", 
        plot_width = 1000,
        plot_height= 500)

    plot_case.title.align = 'center'
    plot_case.title.text_font_size = '20pt'
    plot_case.xgrid.grid_line_color = None
    plot_case.xaxis[0].formatter = DatetimeTickFormatter(seconds = ['%Ss'],minutes = [':%M', '%Mm'])
    plot_case.yaxis[0].formatter = NumeralTickFormatter(format="0.0a")
    plot_case.add_tools(HoverTool(
    tooltips=[( 'Time',  '@pres_timestamp_data{%T}'),('Pressure','@pres_data{‘0,0’}')],
    formatters={'@pres_timestamp_data': 'datetime'}))
    
    plot_case.vbar(x="pres_timestamp_data", top="pres_data", width=300,source = source,color='#78DEC7')
    # plot_case.line(x="pres_timestamp_data", y="pres_data", source = source,line_color="#bd00ff",line_width = 1)
    # plot_case.circle(x="pres_timestamp_data", y="pres_data", source = source, color="#bd00ff", size=8)
    script_pres, div_pres = components(plot_case)

    #Create temp graph

    temps = Temperature.objects.all()
    temp_data,temp_timestamp = [],[]
    for temp in temps:
        temp_value = temp.temp_value
        temp_timestamp.append(temp.timestamp)
        temp_data.append(temp_value)

    temp_timestamp_data = pd.to_datetime(temp_timestamp)
    title = "Temperature"
    source = ColumnDataSource(data=dict(temp_data = temp_data, temp_timestamp_data = temp_timestamp_data ))

    plot_case = figure(title= title , 
        x_axis_label= 'Time', 
        x_axis_type = 'datetime',
        y_axis_label= 'Temperature (°C)',
        # x_range = (0,20),
        tools="pan,wheel_zoom,reset", 
        plot_width = 1000,
        plot_height= 500)

    plot_case.title.align = 'center'
    plot_case.title.text_font_size = '20pt'
    plot_case.xgrid.grid_line_color = None
    plot_case.xaxis[0].formatter = DatetimeTickFormatter(seconds = ['%Ss'],minutes = [':%M', '%Mm'],days = ['%d-%m-%Y', '%F'])
    plot_case.yaxis[0].formatter = NumeralTickFormatter(format="0.0a")
    plot_case.add_tools(HoverTool(
    tooltips=[( 'Time',  '@temp_timestamp_data{%T}'),('Temperature','@temp_data{‘0,0’}')],
    formatters={'@temp_timestamp_data': 'datetime'}))
    
    plot_case.vbar(x="temp_timestamp_data", top="temp_data", width=300,source = source,color='#FF7600')
    # plot_case.line(x="temp_timestamp_data", y="temp_data", source = source,line_color="#bd00ff",line_width = 1)
    # plot_case.circle(x="temp_timestamp_data", y="temp_data", source = source, color="#bd00ff", size=8)
    script_temp, div_temp = components(plot_case)

    args = {
        'script_pres':script_pres,
        'div_pres':div_pres,
        'script_temp':script_temp,
        'div_temp':div_temp,
    }

    return render(request,'opcua_app/graphs.html',args)