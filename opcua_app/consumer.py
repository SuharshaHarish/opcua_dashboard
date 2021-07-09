from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import Temperature,Pressure
from channels.db import database_sync_to_async

class DashConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.groupname='dashboard'
        await self.channel_layer.group_add(
            self.groupname,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self,close_code):

        await self.channel_layer.group_discard(
            self.groupname,
            self.channel_name
        )
    

    async def receive(self, text_data):
        datapoint = json.loads(text_data)
        temperature = datapoint['temperature']
        pressure  = datapoint['pressure']
        
        #save values to database
        await self.save_data(datapoint)

        await self.channel_layer.group_send(
            self.groupname,
            {
                'type':'deprocessing',
                'temperature': temperature,
                'pressure':pressure
            }
        )

        # print ('>>>>',text_data)

    async def deprocessing(self,event):
        temperature = event['temperature']
        pressure  = event['pressure']
        await self.send(text_data=json.dumps({'temperature': temperature,'pressure':pressure}))

    @database_sync_to_async
    def save_data(self, data):
        #save values to database

        temperature = data['temperature']
        pressure  = data['pressure']
        temp = Temperature.objects.create(temp_value = temperature)
        temp.save()

        pres = Pressure.objects.create(pres_value = pressure)
        pres.save()