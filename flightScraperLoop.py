#! python3
# flightScraper.py - loops through tailored json inputs for google flights api

# COMMAND LINE INPUTS
# 1: From Airport
# 2: To Airport
# 3: Number of Days from Today to start looking from
# 4: Number of Days to search
# 5: Email Password

import requests
import datetime
import json
import sys
import pprint
import smtplib

# init smtplib
to = 'mackey.nichols@gmail.com'
gmail_user = 'mackey.nichols@gmail.com'
gmail_pwd = sys.argv[5]

# init url and api key
apiKey = "AIzaSyColmjm796njJk4eoDp24ygH64xkeK0q0E"
url = "https://www.googleapis.com/qpxExpress/v1/trips/search?key="+apiKey

# init vars for json
todayDate = datetime.date.today()
numTickets = 1
origin = sys.argv[1]
destination = sys.argv[2]
daysFromToday = int(sys.argv[3])
daysToSearch = int(sys.argv[4])
numResponses = 50

responses = []

# For each day from today + daysFromToday to today + daysFromToday + daysToSearch
for searchDate in [ datetime.date.today() + datetime.timedelta(days=daysFromToday+i) for i in range(daysToSearch) ]:
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
            "date": searchDate.strftime("%Y-%m-%d")
          }
        ],
            
        #"maxPrice": maxPrice,
        "refundable": "false",
        "solutions": numResponses
      }
    }

    # send json to google flights, parse response json
    r = json.loads(requests.post(url, json = inputJson).text)

    # for each response in this request, summarize the response and add it to responses array
    for i in range(len(r['trips']['tripOption'])):

            thisFlight = {
            "price": r['trips']['tripOption'][i]['saleTotal'],
            "flightNo": r['trips']['tripOption'][i]['slice'][0]['segment'][0]['flight']['carrier']+r['trips']['tripOption'][i]['slice'][0]['segment'][0]['flight']['number'],
            "departureFrom"+origin: r['trips']['tripOption'][i]['slice'][0]['segment'][0]['leg'][0]['departureTime']
            }
                
            responses.append(thisFlight)
            
           
pprint.pprint(responses)

'''
=============
TRASH
=============


weekends = []


if len(sys.argv) < 5:
    departureDay = 4 # Default Friday departure code for below loop
elif sys.argv[4].lower()[:4] == "thurs":
    departureDay = 3
else:
    departureDay = 4 # Default Friday departure code for below loop

# For the next 56 days...
for i in range(14,21):
    

    # If the day's name is Friday, add it to the list
    if (datetime.date.today() + datetime.timedelta(days = i)).weekday() == departureDay:
        thisFriday = datetime.date.today() + datetime.timedelta(days = i)
        thisSunday = datetime.date.today() + datetime.timedelta(days = i+2)
        weekends.append({"friday":thisFriday, "sunday":thisSunday})

# for each search, modify the json, send request for many dates
# send text (and email) if certain criteria are met
    # if cheapest flight of all flights found in this run is less than 2nd command line input, send text!
if float(min(responses, key=lambda x: x['price'])['price'][3:]) < float(sys.argv[2]):
    smtpserver = smtplib.SMTP("smtp.gmail.com",587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(gmail_user, gmail_pwd)
    header = 'To:' + to + '\n' + 'From: ' + gmail_user + '\n' + 'Subject:testing \n'
    msg = header + '\n Cheap flight to '+sys.argv[1]+' found: \n'+min(responses, key=lambda x: x['price'])['flightNo']+' costs '+min(responses, key=lambda x: x['price'])['price']+' and departs '+min(responses, key=lambda x: x['price'])['departureFromYTZ']+ '\n\n'
    smtpserver.sendmail(gmail_user, to, msg)    
    smtpserver.close()

'''

