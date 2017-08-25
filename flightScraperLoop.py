#! python3
# flightScraper.py - loops through tailored json inputs for google flights api

# COMMAND LINE INPUTS
# 1: From Airport
# 2: To Airport
# 3: Number of Days from Today to start looking from
# 4: Number of Days to search
# 5: Number of Flights to return with each email
# 5: Email Password

import requests
import datetime
import json
import sys
import pprint
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# init smtplib and smtpserver
to = 'mackey.nichols@gmail.com'
gmail_user = 'mackey.nichols@gmail.com'
gmail_pwd = sys.argv[6]
smtpserver = smtplib.SMTP("smtp.gmail.com",587)
smtpserver.ehlo()
smtpserver.starttls()
smtpserver.ehlo
smtpserver.login(gmail_user, gmail_pwd)

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
flightsToReturn = int(sys.argv[5])

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
        dateObject = datetime.datetime.strptime(r['trips']['tripOption'][i]['slice'][0]['segment'][0]['leg'][0]['departureTime'][:-6], "%Y-%m-%dT%H:%M")

        date = dateObject.strftime('%A, %B %d, %G at %H:%M')
        dayOfWeek = dateObject.strftime('%A')
        time = dateObject.strftime('%H:%M')
        
        thisFlight = {
        "price": r['trips']['tripOption'][i]['saleTotal'],
        "flightNo": r['trips']['tripOption'][i]['slice'][0]['segment'][0]['flight']['carrier']+r['trips']['tripOption'][i]['slice'][0]['segment'][0]['flight']['number'],
        "departureFromDate": date,
        "departureFromDayofweek": dayOfWeek,
        "departureFromTime": time
        }
            
        responses.append(thisFlight)

           
# Sort reponses by price
goodResponses = sorted(responses, key = lambda k: float(k['price'][3:]) )
bestResponses = [goodResponses[i] for i in range(flightsToReturn)]


# Email top 3 responses
msg = MIMEMultipart('alternative')    

subject = origin+' to '+destination+' Report - Min price: '+bestResponses[0]['price']
msg['Subject'] = subject
msg['From'] = gmail_user
msg['To'] = to

body = '<h3>Last Night\'s '+origin+' -> '+destination+' Flight Report</h3>\n'

for response in bestResponses:
    body += '<b>'+response['flightNo']+'</b>: '+ response['departureFromDate'] + ' costs <i><u>'+response['price']+'</u></i> <br>'  

#msg.attach( MIMEText(header, 'plain') )
msg.attach( MIMEText(body, 'html') )


smtpserver.sendmail(gmail_user, to, msg.as_string())    
smtpserver.close()

# 3: Store all of the responses into some DB
