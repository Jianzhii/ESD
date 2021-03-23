# pip install -r requirements.txt
# https://rapidapi.com/blog/yahoo-finance-api-python/
# seaborn documentation for doing the linegraph - https://seaborn.pydata.org/api.html
# github libraries - gotta see what you need https://github.com/topics/yahoo-finance-api

# pip install yahoo-finance
# https://github.com/lukaszbanasiak/yahoo-finance


# 1. library imports
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import unirest
# change to XML/HTML for API calls
from matplotlib import rcParams

# 2. initialise global data
# store config and transient data
unirest.timeout(15) # 5s timeout

RAPIDAPI_KEY    = "b09591b193mshad22b0d68b19f4ap167b63jsnceb43796bf13" 
RAPIDAPI_HOST = "apidojo-yahoo-finance-v1.p.rapidapi.com"

symbol_string = ""
inputdata = {}

# 3. call API to fetch chart data
def fetchStockData(symbol):

  response = unirest.get("https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/get-charts?region=US&lang=en&symbol=" + symbol + "&interval=1d&range=3mo",
    headers={
      "X-RapidAPI-Host": RAPIDAPI_HOST,
      "X-RapidAPI-Key": RAPIDAPI_KEY,
      "Content-Type": "application/json"
    }
  )

  if(response.code == 200):
    return response.body
  else:
    return None
	# return error?

# 4. Parse API response to show only opening and closing figure for the day
def parseTimestamp(inputdata):

  timestamplist = []

	# for opening figures
  timestamplist.extend(inputdata["chart"]["result"][0]["timestamp"])
	# for closing figures
  timestamplist.extend(inputdata["chart"]["result"][0]["timestamp"])

  calendertime = []

  for ts in timestamplist:
    dt = datetime.fromtimestamp(ts)
    calendertime.append(dt.strftime("%m/%d/%Y"))

  return calendertime

#   4.1. extracting the opening and closing values
def parseValues(inputdata):

  valueList = []
  valueList.extend(inputdata["chart"]["result"][0]["indicators"]["quote"][0]["open"])
  valueList.extend(inputdata["chart"]["result"][0]["indicators"]["quote"][0]["close"])

  return valueList

# 4.2. define the “open” and “close” event
def attachEvents(inputdata):

  eventlist = []

  for i in range(0,len(inputdata["chart"]["result"][0]["timestamp"])):
    eventlist.append("open")    

  for i in range(0,len(inputdata["chart"]["result"][0]["timestamp"])):
    eventlist.append("close")

  return eventlist

# 5. Extract and prepare the data in a Pandas Dataframe

while len(symbol_string) <= 2:
	# take in user data for raw_input
        symbol_string = input("Enter the stock symbol: ")

retdata = fetchStockData(symbol_string)

if (None != inputdata): 

        inputdata["Timestamp"] = parseTimestamp(retdata)

        inputdata["Values"] = parseValues(retdata)

        inputdata["Events"] = attachEvents(retdata)

        df = pd.DataFrame(inputdata)

# 6. Plot the chart
# task 1: define the charting call from the SDK 
# task 2: pass on the styling attributes for displaying the axis and labels.
sns.set(style="darkgrid")

rcParams['figure.figsize'] = 13,5
rcParams['figure.subplot.bottom'] = 0.2

# lineplot() call to Seaborn for rending the chart as a line graph
# how to use lineplot: https://seaborn.pydata.org/generated/seaborn.lineplot.html#seaborn.lineplot
ax = sns.lineplot(x="Timestamp", y="Values", hue="Events",dashes=False, markers=True, 
                   data=df, sort=False)


ax.set_title('Symbol: ' + symbol_string)

plt.xticks(
    rotation=45, 
    horizontalalignment='right',
    fontweight='light',
    fontsize='xx-small'  
)

plt.show()