# Generated by Django 3.2.4 on 2021-07-06 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opcua_app', '0002_alter_temperature_temp_timestamp'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pressure',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pres_value', models.IntegerField(default=0)),
                ('pres_timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
