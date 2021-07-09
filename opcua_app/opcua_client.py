from opcua import Client
import time,json,sys
import websocket
import requests


url = "opc.tcp://192.168.0.246:4840"
client = Client(url)
client.connect()
data = dict()

ws = websocket.WebSocket()
ws.connect('ws://localhost:8000/ws/polData')

try:
    while True:
        temp = client.get_node("ns=2;i=2")
        press = client.get_node("ns=2;i=3")
        temperature = temp.get_value()
        pressure = press.get_value()
        print(pressure, temperature)
        data["temperature"] = int(temperature)
        data["pressure"] = int(pressure)
        ws.send(json.dumps(data))
        time.sleep(2)
except (KeyboardInterrupt,ConnectionResetError):
    client.disconnect()
    print("Client closed")
    sys.exit()
