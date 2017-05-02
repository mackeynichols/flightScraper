#! python3
# flightScraper.py - loops through tailored json inputs for google flights api

import requests
import datetime
import json
import pprint

import twilio

# twilio credentials
account_sid = "AC3ef47f5c8738185a46afd524580cc60b"
auth_token = "3d2e043ad7b55e10c12f9436b7433f22"
twilioClient = twilio.rest.TwilioRestClient(account_sid, auth_token)


# init url and api key
apiKey = "AIzaSyColmjm796njJk4eoDp24ygH64xkeK0q0E"
url = "https://www.googleapis.com/qpxExpress/v1/trips/search?key="+apiKey

# Init dates
# Leave Friday, Return Sunday for the next 8 weekends

# List of Friday and Sunday Dates
weekends = []

# For the next 56 days...
for i in range(14,21):
    
    # If the day's name is Friday, add it to the list
    if (datetime.date.today() + datetime.timedelta(days = i)).weekday() == 4:
        thisFriday = datetime.date.today() + datetime.timedelta(days = i)
        thisSunday = datetime.date.today() + datetime.timedelta(days = i+2)
        weekends.append({"friday":thisFriday, "sunday":thisSunday})


#print(len(fridays))
#print(len(sundays))



# init vars for json
numTickets = 1
origin = "YTZ"
destination = "YUL"
maxPrice = "CAD300"
numResponses = 20
#date = year+"-"+month+"-"+day

responses = []
# For each weekend we search, we send a request
for weekend in weekends:
    # create input json
    inputJson = {
      "request": {
        "passengers": {
          "kind": "qpxexpress#passengerCounts",
          "adultCount": numTickets,
          "infantInLapCount": 0,
          "infantInSeatCount": 0,
          "childCount": 0,
          "seniorCount": 0
        },
        "slice": [
          {
            "kind": "qpxexpress#sliceInput",
            "origin": origin,
            "destination": destination,
            "date": weekend["friday"].strftime("%Y-%m-%d")
          },
          {
            "kind": "qpxexpress#sliceInput",
            "origin": destination,
            "destination": origin,
            "date": weekend["sunday"].strftime("%Y-%m-%d")
          }
        ],
            
        "maxPrice": maxPrice,
        "refundable": "false",
        "solutions": numResponses
      }
    }

    # send json to google flights, parse response json
    r = json.loads(requests.post(url, json = inputJson).text)

    # for each response in this request, find the lowest cost
    for i in range(len(r['trips']['tripOption'])):
        try:

            # ADD ALL RELEVANT INFO FOR EACH FLIGHT INTO AN OBJECT
            # PUT THAT OBJECT INTO A LIST
            thisFlight = {
                "price": r['trips']['tripOption'][i]['saleTotal'],
                "flightNo": r['trips']['tripOption'][i]['slice'][0]['segment'][0]['flight']['carrier']+r['trips']['tripOption'][i]['slice'][0]['segment'][0]['flight']['number'],
                "departureFromYTZ": r['trips']['tripOption'][i]['slice'][0]['segment'][0]['leg'][0]['departureTime']
                }
            
            #pprint.pprint(thisFlight)
            responses.append(thisFlight)
        except:
            pass

    
    # if the lowest cost is below maxPrice var, then send a text
    # text should contain cost, flight number, date, time

    
    # LOOP THROUGH LIST OF OBJECTS, FIND CHEAPEST, EMAIL IT
    # IF FLIGHT IS BELOW A THRESHOLD, TEXT IT

# for each search, modify the json, send request for many dates
# send text (and email) if certain criteria are met

#print(min(responses, key=lambda x: x['price']))
if float(min(responses, key=lambda x: x['price'])['price'][3:]) < 160:
    flight = min(responses, key=lambda x: x['price'])
    twilioClient.messages.create(
        to="+16475457050",
        from_="+13069926945",
        body="CHEAP FLIGHT TO MTL --\n Flight "+ flight['flightNo']+"\nleaving YTZ at "+flight['departureFromYTZ']+"\ncosts "+flight['price']
        )
