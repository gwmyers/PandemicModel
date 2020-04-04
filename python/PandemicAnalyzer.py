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
Analyze data relating to COVID-19 cases reported globally.

Data source:
University of Virginia (http://ncov.bii.virginia.edu/dashboard/)

Alternate data source for model testing:
Johns Hopkins (https://coronavirus.jhu.edu/map.html)
"""
#-------------------------------------------------------------------------
import os
import argparse
import math
import ROOT
import numpy as np
import pandas as pd

#-------------------------------------------------------------------------
# Constants:
#-------------------------------------------------------------------------
DATA_DIR  = '/Users/greg/Desktop/Projects/Nonsense/PandemicModel/data/'
PLOT_DIR  = '/Users/greg/Desktop/Projects/Nonsense/PandemicModel/plots/'

PLACE_KEY = 'Place'
DATA_KEYS_TO_PLOT = ['Confirmed', 'Active']

COUNTRY_KEYS = [
'USA',
'Italy',
'France',
'Switzerland',
'Mainland China',
'Iran',
'Spain',
'South Korea',
]

DOPE_COLOR_PALLETTE = [
ROOT.kBlack,
ROOT.kRed,
ROOT.kGreen,
ROOT.kBlue,
ROOT.kMagenta,
ROOT.kCyan,
ROOT.kOrange,
ROOT.kSpring,
ROOT.kTeal,
ROOT.kAzure,
ROOT.kViolet,
ROOT.kPink,
ROOT.kGray,
ROOT.kYellow,
]

#-------------------------------------------------------------------------
# Functions:
#-------------------------------------------------------------------------
def getDataForCountry(fileString, countryString='USA'):
    '''
    return DataFrame from csv file for specified country
    '''
    df = pd.read_csv(os.path.join(DATA_DIR, fileString), thousands=',')
    
    return df.loc[df[PLACE_KEY] == countryString]

def makePlotFromDataFrameColumn(dataframe, column, tag=''):
    '''
    returns a TH1F created from one column in a DataFrame
    
    x-values: days since Feb 25th
    y-values: column entry for given day (row)
    
    NB: adds 5% error bars to data points to try to estimate uncertainty
    '''
    xData = dataframe[column].tolist()
    nPoints = len(xData)
    h = ROOT.TH1F('h_'+column+'_'+tag, 'h_'+column+'_'+tag, nPoints, 0, nPoints)
    h.SetTitle(tag)
    h.GetYaxis().SetTitle(column)
    h.GetXaxis().SetTitle('days since Feb 25th')
    
    dataScaleFactor  = 1.0
    errorScaleFactor = 0.05
    
    for ii in range(nPoints):
        datum = dataScaleFactor*xData[ii]
        error = errorScaleFactor*datum + math.sqrt(datum)
        h.SetBinContent(ii, datum)
        h.SetBinError(ii, error)
    
    return h

def refreshPad(c):
    c.Modified()
    c.Update()

def formatHistogramForDrawing(histogram, color=ROOT.kBlack, markerStyle=0, lineStyle=0, xlabel='', ylabel=''):
    '''
    sets the format attributes for the histogram passed in
    '''
    histogram.SetMarkerColor(color)
    histogram.SetLineColor(color)
    histogram.SetMarkerStyle(markerStyle)
    histogram.SetLineStyle(lineStyle)
    
    histogram.GetXaxis().SetTitle(xlabel)
    histogram.GetYaxis().SetTitle(ylabel)

def drawPlotOnNewCanvas(plot, tag='', options=''):
    '''
    draws histogram on TCanvas and waits for user to press return to exit
    '''
    c1 = ROOT.TCanvas(tag+'_c1', tag+'_c1', 800, 600)
    c1.cd()
    plot.Draw(options)
    refreshPad(c1)
    input('press <ret> to exit')
    
def drawAllHistogramsInList(hlist, tag):
    '''
    returns a TCanvas with all histograms in given list drawn with option 'same'
    '''
    c1  = ROOT.TCanvas(tag+'_c1', tag+'_c1', 800, 600)
    leg = ROOT.TLegend(0.15, 0.80, 0.30, 0.90)
    c1.cd()
    
    for ii in range(len(hlist)):
        opts = 'hist ep'
        if ii > 0:
            opts += ' same'
        
        markerColor = DOPE_COLOR_PALLETTE[ii] if ii < len(DOPE_COLOR_PALLETTE) else 0
        markerStyle = 20
        lineStyle   = 0
        ylabel      = 'number of cases'
        xlabel      =  hlist[ii].GetXaxis().GetTitle()
        
        formatHistogramForDrawing(hlist[ii], markerColor, markerStyle, lineStyle, xlabel, ylabel)
        hlist[ii].Draw(opts)
        
        legLabel = 'Confirmed' if 'Confirmed' in hlist[ii].GetName() else 'Active'
        leg.AddEntry(hlist[ii], legLabel, 'ep')
        
    refreshPad(c1)
    leg.Draw()
    
    return c1, leg

def makeSummaryPlotsAndSavePDF(fname='case-reports.root', countries=COUNTRY_KEYS, doLogScaleY=False):
    '''
    plots Active and Confirmed cases for each country and saves pdfs
    '''
    rfile = ROOT.TFile(os.path.join(PLOT_DIR, fname), 'read')
    ROOT.gStyle.SetOptStat(0)
    for country in countries:
        nameKey = country+'_cases'
        h_confirmed = rfile.Get('h_'+'Confirmed_'+country)
        h_active    = rfile.Get('h_'+'Active_'+country)
        c, l = drawAllHistogramsInList([h_confirmed, h_active], nameKey)
        
        if doLogScaleY:
            c.SetLogy()
            
        c.SaveAs(os.path.join(PLOT_DIR, nameKey+'.pdf'))
        
    rfile.Close()

#-------------------------------------------------------------------------
# Main:
#-------------------------------------------------------------------------
def main():
    data = pd.DataFrame({'Place':[],
                         'Region':[],
                         'Confirmed':[],
                         'Deaths':[],
                         'Recovered':[],
                         'Active':[],
                         'Last Update':[]})
                         
    nPoints = len([fname for fname in os.listdir(DATA_DIR) if '.csv' in fname ])
    
    f = ROOT.TFile(os.path.join(PLOT_DIR,'case-reports.root'), 'recreate')
    
    for country in COUNTRY_KEYS:
        dfList = []
        for ii in range(nPoints):
            fname = 'COVID-19 Surveillance Dashboard ({0}).csv'.format(ii)
            df = getDataForCountry(fname, country)
            df['Active'] = df['Confirmed'] - df['Recovered'] - df['Deaths']
            dfList.append(df)
            
            data = pd.concat(dfList)
        
        print(data)
        
        for plotKey in DATA_KEYS_TO_PLOT:
            hist = makePlotFromDataFrameColumn(data, plotKey, country)
            hist.Write(hist.GetName())
    
    f.Close()


#-------------------------------------------------------------------------
# Run:
#-------------------------------------------------------------------------
if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description='analyze pandemic data, plot argparser')
        parser.add_argument('-p',action='store_true', required=False, dest='onlyProducePlots', help='save pdfs from root file', default=False)
        parser.add_argument('-l',action='store_true', required=False, dest='doLogScaleY', help='set log scale y-axis', default=False)
        args = parser.parse_args()
        
        if args.onlyProducePlots:
            makeSummaryPlotsAndSavePDF(doLogScaleY=args.doLogScaleY)
        else:
            main()
            makeSummaryPlotsAndSavePDF(doLogScaleY=args.doLogScaleY)
        
    except KeyboardInterrupt:
        print('KeyboardInterrupt\nexiting...')
        exit()
