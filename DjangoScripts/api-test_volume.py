#!/usr/bin/python2.3
# IIT-api-test.py

import re
import urllib
import urllib2
from pprint import pprint
import matplotlib.pyplot as plt
import xml.etree.cElementTree as ElementTree

# Simple test of the Data On Demand HTTP API
# Comment out the plt and matplotlib lines if you dont have it installed...


# XML to Dictionary code source: http://code.activestate.com/recipes/410469-xml-as-dictionary/
# NB: These methods are not appropriate for all XML structures, but work well enough for this example

# Returns a list of dictionries
# Use if you XML contains multiple elements at the same level
class Xml2List(list):
    def __init__(self, aList):
        for element in aList:
            if element:
                # treat like dict
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(Xml2Dict(element))
                # treat like list
                elif element[0].tag == element[1].tag:
                    self.append(Xml2List(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    self.append(text)

# Returns a dictionary
class Xml2Dict(dict):
    '''
    Example usage:

    Given an XML string:

    >>> root = ElementTree.XML(xml_string)
    >>> xmldict = Xml2Dict(root)

    '''
    def __init__(self, parent_element):
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                # treat like dict - we assume that if the first two tags
                # in a series are different, then they are all different.
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = Xml2Dict(element)
                # treat like list - we assume that if the first two tags
                # in a series are the same, then the rest are the same.
                else:
                    # here, we put the list in dictionary; the key is the
                    # tag name the list elements all share in common, and
                    # the value is the list itself
                    aDict = {element[0].tag: Xml2List(element)}
                # if the tag has attributes, add those to the dict
                if element.items():
                    aDict.update(dict(element.items()))
                self.update({element.tag: aDict})
            # this assumes that if you've got an attribute in a tag,
            # you won't be having any text. This may or may not be a
            # good idea -- time will tell.
            elif element.items():
                self.update({element.tag: dict(element.items())})
            # finally, if there are no child tags and no attributes, extract
            # the text
            else:
                self.update({element.tag: element.text})

# See additional endpoints and parameters at: https://www.nasdaqdod.com/
url = 'http://ws.nasdaqdod.com/v1/NASDAQAnalytics.asmx/GetSummarizedTrades'

# Change symbols and date range as needed (not more that 30 days at a time)
values = {'_Token' : '25D26255F6924F31BD86503A4253BEA0',
          'Symbols' : 'AAPL,MSFT',
          'StartDateTime' : '2/1/2015 00:00:00.000',
          'EndDateTime' : '2/18/2015 23:59:59.999',
          'MarketCenters' : '' ,
          'TradePrecision': 'Hour',
          'TradePeriod':'1'}

# Build HTTP request
request_parameters = urllib.urlencode(values)
req = urllib2.Request(url, request_parameters)

# Submit request
try:
    response = urllib2.urlopen(req)

except urllib2.HTTPError as e:
    print(e.code)
    print(e.read())

# Read response
the_page = response.read()

# Remove annoying namespace prefix
the_page = re.sub(' xmlns="[^"]+"', '', the_page, count=1)

# Parse page XML from string
root = ElementTree.XML(the_page)

# Cast ElementTree to list of dictionaries
data = Xml2List(root)

# Package the data into a useful format
hourly_volume = []


# Check for page errors
# I dont use a try/except here because there are a lot of benign errors that can occur (ie non-trading days)
for item in data:
    if item["Outcome"] == 'RequestError' and "Volume" not in item:
        # print("Web Request Error :(  Make sure that you arent pulling more that one month of data. ")
        print(item["Message"])

# Parse the data in sucessful response into a dictionary and compute sums of volume and trades
data_dict = {}
totals = {}
for i in data:
    data_dict[i['Symbol']] = i['SummarizedTrades']['SummarizedTrade']
    totals[i['Symbol']] = {}
    for time_bin in i['SummarizedTrades']['SummarizedTrade']:
        # If key for this time doesnt yet exist create it
        if time_bin['Time'][-12:] not in totals[i['Symbol']].keys():
            totals[i['Symbol']][str(time_bin['Time'][-12:])] = {'Volume':int(time_bin['Volume']), 'Trades':int(time_bin['Trades'])}
        # Otherwise add the current value to the running total
        else:
            totals[i['Symbol']][str(time_bin['Time'][-12:])]['Volume'] += int(time_bin['Volume'])
            totals[i['Symbol']][str(time_bin['Time'][-12:])]['Trades'] += int(time_bin['Trades'])

# Examine dictionary
pprint(totals)

# initialize some variables needed for plotting
colors = ['b','r','y','g']
counter = 0
width=0.2

# Convert data into lists and sort it for plotting
for t in totals:
    pprint(t)
    times = []
    volumes = []
    for key in totals[t]:
        times.append(key)
        volumes.append(totals[t][key]['Volume'])

    # Zip the lists together
    merged = zip(times,volumes)
    # Sort by time ascending
    merged.sort()
    # Split them back apart
    times, volumes = zip(*merged)
    # Compunt the x offset for subsequent columns in the bar chant (otherwise, bars will overlap)
    x_pos = [x-(counter*width) for x in range(len(volumes))]
    # Add the data to the plot
    plt.bar(x_pos, volumes, width=width, label=t, color=colors[counter%3], align='center')

    counter += 1
# Configure plot options
plt.xticks(range(len(times)), [x[0:5] for x in times], rotation='vertical')
plt.legend(loc=2)
plt.title(format("Comparison of Volumes for %s" % (str(totals.keys()).strip('[').strip(']'))))
plt.xlabel("Time of Day (by hour)")
plt.ylabel(format("Shares traded over date range:\n %s to %s" % (str(values['StartDateTime']), str(values['EndDateTime']))))
# Display
plt.show()

plt.close()
