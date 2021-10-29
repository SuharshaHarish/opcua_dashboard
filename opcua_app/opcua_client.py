from opcua import Client
import time,json,sys
import websocket,socket
import requests
from datetime import datetime,timedelta

url = "opc.tcp://192.168.0.246:4840"
client = Client(url)

def connection_loop():
    client.connect()
    data = dict()
    ws = websocket.WebSocket()
    ws.connect('ws://localhost:8000/ws/polData')
    while True:
        try:
            temp = client.get_node("ns=2;i=2")
            press = client.get_node("ns=2;i=3")
            temperature = temp.get_value()
            pressure = press.get_value()
            print(pressure, temperature)
            data["temperature"] = int(temperature)
            data["pressure"] = int(pressure)
            ws.send(json.dumps(data))
            time.sleep(2)
        except Exception as e:            
            print("Caught ",e.__class__.__name__)
            handle_error(e)
            break

def handle_error(e):

    current_time = datetime(year=2021,month=10,day=29,hour=8,minute=59,second=45)
    # current_time = datetime.now()

    if current_time.hour < 9:
        start = datetime(year=current_time.year,month=current_time.month,day=current_time.day,hour=9)
        waiting_time = start-current_time
        print("Retrying Connection in {0} seconds".format(waiting_time.total_seconds()))
        time.sleep(waiting_time.total_seconds())
        print("Trying to connect...")

    elif current_time.hour >= 17:
        next_day = datetime(year=current_time.year,month=current_time.month,day=current_time.day) + timedelta(days=1)
        start = datetime(year=next_day.year,month=next_day.month,day=next_day.day,hour=9)
        waiting_time = start-current_time
        print("Retrying Connection in {0} seconds".format(waiting_time.total_seconds()))
        time.sleep(waiting_time.total_seconds())
        print("Trying to connect...")

    else:       
        print("Retrying Connection in 10 seconds") 
        print("Trying to connect...")
        time.sleep(10)

while True:   
    try:        
        connection_loop()

    except (KeyboardInterrupt):
        client.disconnect()
        print("Client closed")
        sys.exit()

    # except(ConnectionResetError):
    #     client.disconnect()
    #     print("Client closed test")
    #     sys.exit()

    except Exception as e:
        # client.disconnect()
        # print("Connection Refused by dashboard Client closed") 
        print("Server unavailable")    
        handle_error(e)

# Use ctrl+fn+b if terminal freezes