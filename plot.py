import plotly.plotly as py
import plotly.graph_objs as go
import csv
import numpy as np

from numpy import genfromtxt

alldata = genfromtxt('log.csv',delimiter=',')
sp = alldata[:,0]

data = [go.Histogram(x=sp)]

py.plot(data, filename='Speed Logs', auto_open=False)
