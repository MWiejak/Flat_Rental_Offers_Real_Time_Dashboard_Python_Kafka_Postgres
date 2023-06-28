from bs4 import BeautifulSoup
import requests
import re
import datetime
import json
import time
from confluent_kafka import Producer

#Kafka configuration
bootstrap_servers = "host.docker.internal:29092" #'127.0.0.1:9092'
topic = 'test'
producer = Producer({'bootstrap.servers': bootstrap_servers})

# Function to send message to Kafka topic
def send_message(key,data):
    try:
        print("Sending offer to kafka server...")
        producer.produce(topic, key=key, value=data)
        producer.flush()
        print("Offer sent!")

    except Exception as ex:
        print("Error while sending message")
        print(str(ex))

#Getting offers data
def get_flats():
    try:
        print("Getting offers...")
        html_text = requests.get('https://www.olx.pl/warszawa/q-mieszkanie-do-wynajęcia/?search%5Border%5D=created_at:desc').text
        soup = BeautifulSoup(html_text,features="html.parser")
        pages = soup.find_all('a', class_ = 'css-1mi714g', href = True )
        last_page = int(str(pages[len(pages)-1].text))
        url = 'https://www.olx.pl/warszawa/q-mieszkanie-do-wynajęcia/?page=<NUMBER>&search%5Border%5D=created_at%3Adesc'
        flats = []

        for i in range(1,last_page+1):
            html_text = requests.get(url.replace('<NUMBER>',str(i))).text
            soup = BeautifulSoup(html_text,features="html.parser")
            flats_page = soup.find_all('div', class_ = 'css-1sw7q4x')

            for flat in flats_page:
                flats.append(flat)
        print("Offers scraped successfully!")
        return flats
    
    except Exception as ex:
        print('Exception in getting offers')
        print(str(ex))

# Filtering and extracting relevant data - publish date, size, location and price for rental offers that are maxium <time_span> days old
def process_offer (flat, time_span = 14, max_price = 100001):
    try:
        month_dict = {
            "stycz":1,
            "lut":2,
            "mar":3,
            "kwie":4,
            "maj":5,
            "czerw":6,
            "lip":7,
            "sierp":8,
            "wrze":9,
            "pa":10,
            "listopad":11,
            "grud":12
        }
        location_date_obj = flat.find('p', class_ ='css-veheph er34gjf0')

        if location_date_obj is not None:
            location_date = location_date_obj.text
            now = datetime.datetime.now()
            today = datetime.datetime(now.year, now.month, now.day)
            date = None

            if re.search("dzisiaj",location_date, re.IGNORECASE):
                date = today

            else:
                datear = re.findall(r'(\d+ \w+\ \d+)',location_date)[0].split(' ')
                day = int(datear[0])
                monthstr = datear[1]
                month = -1
                year = int(datear[2])
    
                if datetime.datetime.now().date().year == year:

                    for key in month_dict:
                        if re.search(key,monthstr):
                            month = month_dict[key] 
                            break
                    
                    date = datetime.datetime(year,month,day)



            if (today - date).days <= time_span:
                price_obj = flat.find('p', class_ = 'css-10b0gli er34gjf0')

                if price_obj is not None:
                    
                    price_text = price_obj.text
                    price = -1

                    if price_text == "Za darmo":
                        price = 0

                    else:
                        price = int(''.join(re.findall(r'\d+', price_text)))

                    if price < max_price:
                        
                        location = re.findall(r'Warszawa,\ (\w+-?\w+)', location_date)[0] if re.search(',',location_date) else 'Warsaw'

                        try:
                            size_text = flat.find('span', class_ = 'css-643j0o').text
                            size = -1.0

                            if(re.search(r'\d+,\d+', size_text)):
                                size = float(re.findall(r'\d+,\d+', size_text)[0].replace(",","."))
                            else:
                        
                                size = float(''.join(re.findall(r'\d+', size_text)))
                        except:
                            size = -1.0

                        url_beggining = "https://www.olx.pl"
                        url_end = re.findall(r'href=\"(.+.html)', str(flat))[0]
                        url = ""
                        if re.search('https',url_end):
                            url = url_end
                        else:
                            url = url_beggining+url_end
                            
                        row = {'date':str(date).replace("00:00:00",""),'location':location,'size':size,'price':price,'url':url}
                        send_message(url,json.dumps(row))
    except Exception as ex:
        print("Exception while processing offer")
        print(str(ex))


if __name__ == '__main__':

    while True:
        flats = get_flats()
        print("Processing, and sending offers...")

        for offer in flats:
            process_offer(offer)

        print("Offers processed!")
        time.sleep(60)