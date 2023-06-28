# Flat_Rental_Offers_Real_Time_Dashboard_Python_Kafka_Postgres
This repository contains a real-time dashboard of flat rental offers in Warsaw, scraped from ww.olx.pl website.It uses Kafka server for storing new offers, and Postgres server containing all scraped flats for analysis purposes.
This project was created as a group project for Advanced Data Analytics graduate studies. I am responsible for creating web scraping, storing data to kafka server, then retreiving it and processing by consumer. I also was responsible for setting up zookeeper, kafka and Postgres servers. Additionaly I dockerized producer, consumer and servers.
To run the project:
1. Pull and run required docker images by running 'docker compose up' command inside the main project folder.
2. Wait around a minute for the data to be uploaded to Postgres server
3. run app.py script and go to the http://127.0.0.1:8050/ address.
