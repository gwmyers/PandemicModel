#! /usr/bin/env python
#-------------------------------------------------------------------------
# File: PandemicAnalyzer.py
# Author: Greg Myers
# Created: 3/16/20 
#
# Description:
#
#

"""
Analyze data from WHO on COVID-19 cases reported globally
"""
#-------------------------------------------------------------------------
import os
import ROOT
import numpy as np
import pandas as pd

#-------------------------------------------------------------------------
# Constants:
#-------------------------------------------------------------------------
URL_WHO   = 'https://www.who.int/emergencies/diseases/novel-coronavirus-2019/situation-reports'
URL_UVIRG = 'http://ncov.bii.virginia.edu/dashboard/'
DATA_DIR  = 'data/'

DATA_KEYS = ['Place', 'Region', 'Confirmed', 'Deaths', 'Recovered', 'Last Update']
PLACE_KEY = 'Place'
DATE_KEY  = 'Last Update'

#-------------------------------------------------------------------------
# Functions:
#-------------------------------------------------------------------------
def getDataForCountry(fileString):
    df = pd.read_csv(os.path.join(DATA_DIR, fileString), thousands=',')
    
    return df.loc[df[PLACE_KEY] == 'USA']

def makePlotFromDataFrameColumn(dataframe, column):
    xData = dataframe[column].tolist()
    nPoints = len(xData)
    h = ROOT.TH1F('h_'+column, 'h_'+column, nPoints, 0, nPoints)
    
    for ii in range(nPoints):
        h.SetBinContent(ii, xData[ii])
    
    return h

def updateCanvas(c):
    c.Modified()
    c.Update()

def drawPlotOnNewCanvas(plot, tag='', options=''):
    c1 = ROOT.TCanvas(tag+'_c1', tag+'_c1', 800, 600)
    c1.cd()
    plot.Draw(options)
    updateCanvas(c1)
    input('press <ret> to exit')

#-------------------------------------------------------------------------
# Main:
#-------------------------------------------------------------------------
def main():
    data = pd.DataFrame({'Place':[],
                         'Region':[],
                         'Confirmed':[],
                         'Deaths':[],
                         'Recovered':[],
                         'Last Update':[]})
    nPoints = 19
    d = []
    for ii in range(nPoints):
        fname = 'COVID-19 Surveillance Dashboard ({0}).csv'.format(ii)
        d.append(getDataForCountry(fname))
        data = pd.concat(d)
    
    print(data)
    
    hist = makePlotFromDataFrameColumn(data, 'Confirmed')
    drawPlotOnNewCanvas(hist, options='hist ep')
    
    f = ROOT.TFile('test.root', 'new')
    hist.Write(hist.GetName())
    f.Close()
    


#-------------------------------------------------------------------------
# Run:
#-------------------------------------------------------------------------
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('KeyboardInterrupt\nexiting...')
        exit()
