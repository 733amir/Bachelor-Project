import paho.mqtt.client as mqtt
from json import dumps as tojson, loads as fromjson
from time import sleep
from random import randrange
from threading import Thread


class SimulatedDevice:
    # In this simulation we use a server, a gateway and four devices.
    #  ID  | What is does?
    # -------------------------------------------------------------------------
    #   1  | Server that get data and send them where they should go.
    #   2  | Gateway that get data and send them where they should go.
    #  3,4 | Generate simulated temperature and light sensors data.
    #   5  | Generate simulated temperature, light and RFID sensors data.
    #   6  | Collect data of temperature, light and RFID sensors and display them on a monitor.
    def log(self, message, level=0):
        print("{}{} => {}".format(level*'  ', 'Device [{}]'.format(self.config['id']), message))

    def get_configuration(self):
        return tojson({
            'id': self.config['id'],
            'pid': self.config['parent-id']
        })

    def __init__(self, config, LCD=False, LDR_LM35=False, RFID=False):
        self.config, self.lcd, self.ldr_lm35, self.rfid = config, LCD, LDR_LM35, RFID
        self.log('Created with config: {}'.format(self.config))

        self.PHELLO = '[HELLO]{}'.format(config['parent-id'])
        self.PBYE = '[BYE]{}'.format(config['parent-id'])
        self.PINF = '[INF]{}'.format(self.config['parent-id'])
        self.PCMD = '[CMD]{}'.format(self.config['parent-id'])

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(self.config['parent-mqtt-broker/ip'],
                            self.config['parent-mqtt-broker/port'],
                            self.config['keep-alive'])

        while True:
            self.client.loop()
            self.publish()
            sleep(1)

    def on_connect(self, client, userdata, flags, rc):
        self.client.publish(self.PHELLO, self.get_configuration(), qos=1)
        self.client.subscribe(self.PCMD, qos=1)
        if self.lcd:
            self.client.subscribe(self.PINF, qos=1)

    def on_message(self, client, userdata, msg):
        topic, payload = msg.topic, fromjson(msg.payload.decode())
        self.log('Message received from child. topic: {}, payload: {}'.format(topic, payload))

        if topic == self.PCMD:
            pass
        elif self.lcd and topic == self.PINF:
            if self.config['id'] in payload['to']:
                self.log('LCD => {}'.format(payload['data']))

    def publish(self):
        if self.ldr_lm35:
            self.client.publish(self.PINF, tojson({
                'id': self.config['id'],
                'data': {'ldr': randrange(1, 10),
                         'lm35': randrange(1, 10)},
                'to': [6]
            }), qos=1)
        if self.rfid:
            self.client.publish(self.PINF, tojson({
                'id': self.config['id'],
                'data': {'rfid': randrange(1000000, 9999999)},
                'to': [6]
            }), qos=1)


if __name__ == '__main__':
    ############################## Single Multi-purpose Device ##############################
    SimulatedDevice(config={
        'id': 2,
        'group-id': 2,
        'type': 'device',
        'keep-alive': 60,
        'local-mqtt-broker/ip': 'localhost',
        'local-mqtt-broker/port': 1883,

        'parent-id': 1,
        'parent-mqtt-broker/ip': 'localhost',
        'parent-mqtt-broker/port': 1883,
    }, LDR_LM35=True, RFID=True, LCD=True)

    ############################## One temperature and light sensor enabled device connected to gateway
    # and one LCD enabled device connected to server.
    Thread(target=SimulatedDevice, args=[{
        'id': 3,
        'group-id': 3,
        'type': 'device',
        'keep-alive': 60,
        'local-mqtt-broker/ip': 'localhost',
        'local-mqtt-broker/port': 1883,

        'parent-id': 2,
        'parent-mqtt-broker/ip': 'localhost',
        'parent-mqtt-broker/port': 1883,
    }, False, True, True]).start()

    SimulatedDevice(config={
        'id': 6,
        'group-id': 6,
        'type': 'device',
        'keep-alive': 60,
        'local-mqtt-broker/ip': 'localhost',
        'local-mqtt-broker/port': 1883,

        'parent-id': 1,
        'parent-mqtt-broker/ip': 'localhost',
        'parent-mqtt-broker/port': 1883,
    }, LCD=True)
