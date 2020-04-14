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
'Taiwan',
'Germany',
'United Kingdom',
'India',
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
# Data Preparation:
#-------------------------------------------------------------------------
def getDataForCountry(fileString, countryString='USA'):
    '''
    return DataFrame from csv file for specified country
    '''
    df = pd.read_csv(os.path.join(DATA_DIR, fileString), thousands=',')
    
    return df.loc[df[PLACE_KEY] == countryString]

def makeHistogramFromDataFrameColumn(dataframe, column, tag=''):
    '''
    returns a TH1F created from one column in a DataFrame
    
    x-values: days since Feb 25th
    y-values: column entry for given day (row)
    
    NB: adds 10% error bars to data points to try to estimate uncertainty
    '''
    xData = dataframe[column].tolist()
    nPoints = len(xData)
    h = ROOT.TH1F('h_'+column+'_'+tag, 'h_'+column+'_'+tag, nPoints+1, 0, nPoints+1)
    h.SetTitle(tag)
    h.GetYaxis().SetTitle(column)
    h.GetXaxis().SetTitle('days since Feb 25th')
    
    dataScaleFactor  = 1.0
    errorScaleFactor = 0.10
    
    for ii in range(nPoints):
        datum = dataScaleFactor*xData[ii]
        error = errorScaleFactor*datum + math.sqrt(datum)
        # zeroth bin is underflow bin, so add 1:
        h.SetBinContent(ii+1, datum)
        h.SetBinError(ii+1, error)
    
    return h

#-------------------------------------------------------------------------
# Plotting:
#-------------------------------------------------------------------------
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
    returns a TCanvas and legend with all histograms in given list drawn with option 'same'
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

def makeAllHistograms():
    '''
    prep data and save hitograms to .root file
    '''
    data = pd.DataFrame({'Place':[],
                         'Region':[],
                         'Confirmed':[],
                         'Deaths':[],
                         'Recovered':[],
                         'Active':[],
                         'Last Update':[]})
                         
    nPoints = len([fname for fname in os.listdir(DATA_DIR) if '.csv' in fname ])
        
    f = ROOT.TFile(os.path.join(PLOT_DIR,'case-reports.root'), 'recreate')
    
    print("number of data points found: {0}".format(nPoints))
    
    for country in COUNTRY_KEYS:
        print("making plot for country: {0}".format(country))
        dfList = []
        for ii in range(nPoints):
            fname = 'COVID-19 Surveillance Dashboard ({0}).csv'.format(ii)
            df = getDataForCountry(fname, country)
            df['Active'] = df['Confirmed'] - df['Recovered'] - df['Deaths']
            dfList.append(df)
            
            data = pd.concat(dfList, sort=True)
        
        #print(data)
        
        for plotKey in DATA_KEYS_TO_PLOT:
            hist = makeHistogramFromDataFrameColumn(data, plotKey, country)
            hist.Write(hist.GetName())
    
    f.Close()

#-------------------------------------------------------------------------
# Analysis:
#-------------------------------------------------------------------------
def runAnalysis():
    '''
    performs a simple logistic fit to number of confirmed cases in US
    '''
    ROOT.gStyle.SetOptFit(1111)
    # get the histogram to analyze
    rfile = ROOT.TFile(os.path.join(PLOT_DIR,'case-reports.root'), 'read')
    hist  = rfile.Get('h_Confirmed_USA')
    nBins = hist.GetNbinsX()
    
    # format the histogram:
    markerColor = ROOT.kBlack
    markerStyle = 20
    lineStyle   = 0
    xlabel      = hist.GetXaxis().GetTitle()
    ylabel      = 'number of confirmed cases'
    formatHistogramForDrawing(hist, markerColor, markerStyle, lineStyle, xlabel, ylabel)
   
    # define fit function:
    logisticFunc = ROOT.TF1('logisticFunc','[0]/( 1 + [1]*exp(-[2]*(x-[3])) )', 0, nBins+1)
    logisticFunc.SetParameters(1,1,1,0)
    logisticFunc.SetLineColor(ROOT.kMagenta)
    
    # do the fit:
    hist.Fit(logisticFunc, '', '',9, nBins)
    
    # draw the histogram and fit function together:
    c1 = ROOT.TCanvas('c1', 'c1', 800, 600)
    leg = ROOT.TLegend(0.45, 0.80, 0.67, 0.90)
    
    c1.SetLogy()
    c1.cd()
    logisticFunc.Draw()
    hist.Draw()
    refreshPad(c1)
    
    leg.AddEntry(logisticFunc, '#frac{p_{0}}{1+p_{1}exp#left[-p_{2}(x-p_{3})#right]}','l')
    leg.Draw()
    
    # move the damn stats box out of the way:
    ps = hist.GetListOfFunctions().FindObject('stats')
    ps.SetX1NDC(0.15)
    ps.SetX2NDC(0.45)
    ps.SetY1NDC(0.55)
    ps.SetY2NDC(0.90)
    refreshPad(c1)
    
    #input('press <ret> to exit')
    c1.SaveAs(os.path.join(PLOT_DIR,'USA_LogisticFit_To_Confirmed_Cases.pdf'))
    
    rfile.Close()


#-------------------------------------------------------------------------
# Run:
#-------------------------------------------------------------------------
if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description='analyze pandemic data - plotting and fitting')
        parser.add_argument('-p',action='store_true', required=False, dest='doOnlyDataPrep', help='make histograms from data files', default=False)
        parser.add_argument('-s',action='store_true', required=False, dest='doOnlySavePlots', help='make plots and save pdfs', default=False)
        parser.add_argument('-a',action='store_true', required=False, dest='doOnlyAnalysis', help='run fit to data', default=False)
        args = parser.parse_args()
        
        doSetLogy = True
        
        if args.doOnlyDataPrep:
            makeAllHistograms()
        elif args.doOnlyAnalysis:
            runAnalysis()
        elif args.doOnlySavePlots:
            makeSummaryPlotsAndSavePDF(doLogScaleY=doSetLogy)
        else:
            makeAllHistograms()
            makeSummaryPlotsAndSavePDF(doLogScaleY=doSetLogy)
            runAnalysis()
        
    except KeyboardInterrupt:
        print('KeyboardInterrupt\nexiting...')
        exit()
