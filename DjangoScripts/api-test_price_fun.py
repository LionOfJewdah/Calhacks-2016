#!/usr/bin/python2.3
# mit-api-test-http.py

import urllib
import urllib2
import xml.etree.cElementTree as ElementTree
import re
import sys
import io
from pprint import pprint
import datetime as dt
import MySQLdb

# Simple test of the Data On Demand HTTP API
# Comment out the plt and matplotlib lines if you dont have it installed...


#XML to Dictionary code source: http://code.activestate.com/recipes/410469-xml-as-dictionary/

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


## API Test ##

url = 'http://ws.nasdaqdod.com/v1/NASDAQAnalytics.asmx/GetEndOfDayData'
startDate = sys.argv[1].split('/')
endDate = sys.argv[2].split('/')

startMonth = int(startDate[0])
startDay = int(startDate[1])
startYear = int(startDate[2])

endMonth = int(endDate[0])
endDay = int(endDate[1])
endYear = int(endDate[2])

# get the values and store them 10 times, over 17 day spans
for jvar in range (0, 10) :
	print("Run %d." % (jvar + 1))
	
	d1 = dt.date(startYear, startMonth, startDay) + dt.timedelta(18 * jvar)
	d2 = dt.date(endYear, endMonth, endDay) + dt.timedelta(18 * jvar)
	# Change symbols and date range (not more that 30 days at a time)
	values = {'_Token' : '25D26255F6924F31BD86503A4253BEA0',
			  'Symbols' : 'GOOG',
			#   'StartDate' : '9/1/2015' + (18 * jvar),
			#   'EndDate' : '9/18/2015' + (18 * jvar),
			#   'StartDate' : (date(2015, 9, 1) + (18 * jvar)).__format__("%m/%d/%Y")
			#   'EndDate' : (date(2015, 9, 18) + (18 * jvar)).__format__("%m/%d/%Y")
			  'StartDate' : d1.__format__("%m/%d/%Y"),
			  'EndDate' : d2.__format__("%m/%d/%Y"),
			  'MarketCenters' : '' }

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
	closing_prices = []

	#print data

	if data[0]["Outcome"] == 'RequestError' and "Prices" not in data[0]:
		print("Web Request Error :(  Make sure that you arent pulling more that one month of data. ")
		print(the_page)

	stockPredix = MySQLdb.connect("127.0.0.1", "admin", "ScrabbleSquad9", "StockPredix")
	cursor = stockPredix.cursor()
	cursor.execute("delete from endofday")
	cursor.execute("delete from summaryinfo")

	for i in data:
		closing_prices.append({'Symbol':i['Symbol'],'Dates':[],'Prices':[], 'PercentChange':[]})

		for price in i['Prices']['EndOfDayPrice']:
			if (type(price) is str or price['Outcome'] == 'RequestError'):
				continue
			priceDate = price['Date'].split('/')
			month = priceDate[0]
			day = priceDate[1]
			year = priceDate[2]
			try:
				endOfDaySql = "insert into endofday (date, close, open, high, low, lastsale, volume) values (\'%s-%s-%s 00:00:00\', %s, %s, %s, %s, %s, %s)" % (year, month, day, price['Close'], price['Open'], price['High'], price['Low'], price['LastSale'], price['Volume'])
				print endOfDaySql
				cursor.execute(endOfDaySql)

			except(Exception) as e:
				print("Error with executing SQL: %s" % e)

			try:
				closing_prices[-1]['Dates'].append(price['Date'])
				closing_prices[-1]['Prices'].append(float(price['Close']))

				## Normalize prices to show percent change from start of time range
				closing_prices[-1]['PercentChange'].append(100*(closing_prices[-1]['Prices'][-1]-
					closing_prices[-1]['Prices'][0])/
					closing_prices[-1]['Prices'][0])

			except(Exception) as e:
				print("Skipping non-trading date.")

	# Examine new dictionary
	closing_price = closing_prices[0]
	for i in range(0, len(closing_price['Dates'])):
		priceDate = closing_price['Dates'][i].split('/')
		month = priceDate[0]
		day = priceDate[1]
		year = priceDate[2]
		try:
			summarySql = "insert into summaryinfo (date, percent_change, prices, symbol) values (\'%s-%s-%s 00:00:00\', %s, %s, \'%s\')" % (year, month, day, closing_price['PercentChange'][i], closing_price['Prices'][i], closing_price['Symbol'])
			print summarySql
			cursor.execute(summaryinfo)

		except(Exception) as e:
			print("Error with executing SQL: %s" % e)

	stockPredix.commit()
stockPredix.close()
response.close()

