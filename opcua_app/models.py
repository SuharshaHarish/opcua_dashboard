from django.db import models
from django.db.models.deletion import CASCADE
from django.utils import timezone 

class Temperature(models.Model):

    temp_value = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.temp_value)

class Pressure(models.Model):

    pres_value = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.pres_value)

class Anomaly(models.Model):

    PARAM_CHOICES = (
        ('t','Temperature'),
        ('p','Pressure')
    )
    param_type = models.CharField(choices=PARAM_CHOICES,null=False,max_length=20)
    pres_key = models.ForeignKey(Pressure,on_delete=CASCADE,null=True)
    temp_key = models.ForeignKey(Temperature,on_delete=CASCADE,null=True)

    def __str__(self):

        if self.param_type == 't':

            return ("Temperature "+str(self.temp_key.timestamp))
        else:

            return ("Pressure "+str(self.pres_key.timestamp))

