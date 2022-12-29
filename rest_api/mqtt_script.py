#!/home/phat/rest_api_env/bin/python

import django
import os
import paho.mqtt.client as paho
from paho import mqtt
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rest_api.settings")


if __name__ == '__main__':

    django.setup()
    from django.conf import settings
    from users.models import location
    from users.serializers import LocationSerializer
    from users.models import location, item

    def on_connect(client, userdata, flags, rc, properties=None):
        if rc == 0:
            client.subscribe("devices_GPS/#", qos=0)
            client.subscribe("devices_control/#", qos=0)
            client.subscribe("test/#", qos=0)
            print("CONNACK received with code %s." % rc)
        else:
            print("Bad connection: ", rc)

    def on_publish(client, userdata, mid, properties=None):
        print("mid: " + str(mid))

    def on_subscribe(client, userdata, mid, granted_qos, properties=None):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_message(client, userdata, msg):
        device_topic = msg.topic.rsplit('/')
        # khung topic device_GPS/IMEI
        if device_topic[0] == 'devices_GPS':
            # khung ban tin: 123.12345/123.12345/imeiimeiimei/
            content = msg.payload.decode("utf-8")
            list = content.rsplit('/')

            if len(list) == 3 and device_topic[1] == list[2]:
                try:
                    device = item.objects.get(IMEI=list[2])
                    device_id = device.id
                    payload = {
                        'lat': float(list[0]),
                        'lng': float(list[1]),
                        'original_item': device_id
                    }
                    serializer = LocationSerializer(data=payload)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    print(payload)
                except:
                    print("Cannot save your messages")
            else:
                print("Cannot save your messages, wrong topic")
        elif device_topic[0] == 'devices_control':
            # khung ban tin: imeiimeiimei/0-1
            content = msg.payload.decode("utf-8")
            list = content.rsplit('/')
            if len(list) == 2 and device_topic[1] == list[0]:
                if list[1] == '1':
                    device_condition = True
                elif list[1]=='0':
                    device_condition = False
                try:
                    device = item.objects.get(IMEI=list[0])
                    device_id = device.id
                    payload = {
                        'id': device_id,
                        'condition': device_condition
                    }
                    print(payload)
                    device.condition = device_condition
                    device.save()

                except:
                    print("Cannot save your messages")
            else:
                print("Cannot save your messages, wrong topic")
        else:
            print(msg.payload)

    client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
    client.on_connect = on_connect

   #client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)

   #client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASSWORD)

    client.connect(
        host=settings.MQTT_SERVER,
        port=settings.MQTT_PORT,
        keepalive=settings.MQTT_KEEPALIVE
    )

    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.on_publish = on_publish
    client.publish("test/1", payload="successfully connected", qos=0)    
    client.loop_forever()
