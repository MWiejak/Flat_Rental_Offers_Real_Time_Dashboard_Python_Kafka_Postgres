from confluent_kafka import Consumer
from time import sleep
from json import loads
from datetime import datetime
from connect import connect
from table_creation import create_table_if_doesnt_exist

# Kafka configuration
bootstrap_servers = "host.docker.internal:29092" 
#bootstrap_servers ='127.0.01:9092'
topic = 'test'
group_id = '0'

# Kafka consumer configuration
consumer_config = {
    'bootstrap.servers': bootstrap_servers,
    'group.id': group_id,
    'auto.offset.reset': 'earliest'
}

# Create Kafka consumer
try:
    print("Establishing connection to kafka server...")

    consumer = Consumer(consumer_config)
    consumer.subscribe([topic])

    print("Connection established!")

except Exception as e:
    print("Error while trying to establish kafka server connection")
    print(str(e))

# Create PostgreSQL database connection using connect.py script:

try:
    print("Establishing connection to PostgreSQL server...")
    sleep(10)
    conn = connect()
    cursor = conn.cursor()

    print("Connection established!")
    
except Exception as e:
    print("Error while trying to establish PostgreSQL server connection")
    print(str(e))

# Start consuming messages
if __name__ == '__main__':
    create_table_if_doesnt_exist()
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue
        try:
            # Parse the message value as the data to be inserted
            data = eval(msg.value().decode('utf-8'))

            print(f"Processing message: {data}")

            insert_query = "INSERT INTO flats VALUES (%s, %s, %s, %s, %s)"
            values = (data['url'], data['location'], data['date'],data['size'],data['price'])
            cursor.execute(insert_query, values)
            conn.commit() 

            print("Message processed!")

        except Exception as e:
            print(f"Error processing message: {e}")
            conn.rollback()