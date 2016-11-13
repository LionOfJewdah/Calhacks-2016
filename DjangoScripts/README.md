# Nasdaq Data-On-Demand
Nasdaq Data-On-Demand is a cloud-based computing solution that provides easy and flexible access to large amounts of high quality and reliable historical Level 1 data for Nasdaq, NYSE, and other regional-listed securities for sub-second tick-by-tick quotes dating back to January 1, 2008.
### Analytics
* End of Day Data
* Volume Weighted Average Price (VWAP)
* Time Weighted Average Price (TWAP)
* Average Market Spreads
* Crossed and Locked Market Quotes
* Quote Highs and Lows
* Summarized Trades

### Quotes & Trades
* Bid Quantity
* Bid Price
* Market Center
* Ask Quantity
* Ask Price
* Pre-Market Quotes
* Post-Market Quotes
* Quote Condition

#### Documentation
> [Full API.](http://www.nasdaqdod.com/NASDAQAnalytics.asmx?v=xOperations) 

> [Sample data.](http://www.nasdaqdod.com/Samples.aspx)



Simple test of the Data On Demand HTTP API
```python
import re
import urllib
import urllib2
import xml.etree.cElementTree as ElementTree

# See additional endpoints and parameters at: https://www.nasdaqdod.com/ 
url = 'http://ws.nasdaqdod.com/v1/NASDAQAnalytics.asmx/GetSummarizedTrades'

# Change symbols and date range as needed (not more that 30 days at a time)
values = {'_Token' : 'BC2B181CF93B441D8C6342120EB0C971',
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

# Parse page XML from string
root = ElementTree.XML(the_page)

# DO SOMETHING....
```
