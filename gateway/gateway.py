from threading import Thread

import paho.mqtt.client as mqtt
from json import dumps as tojson, loads as fromjson
from tree import Tree, IdentificationError
from time import sleep


class Gateway:
    def log(self, message, level=0):
        print("{}{} => {}".format(level*'  ', 'Gateway [{}]'.format(self.config['id']), message))

    def get_configuration(self):
        return tojson({
            'id': self.config['id'],
            'pid': self.config['parent-id']
        })

    def __init__(self, config):
        self.config = config
        self.log('Created with config: {}'.format(self.config))

        self.HELLO = '[HELLO]{}'.format(self.config['id'])
        self.BYE = '[BYE]{}'.format(self.config['id'])
        self.INF = '[INF]{}'.format(self.config['id'])
        self.CMD = '[CMD]{}'.format(self.config['id'])

        self.PHELLO = '[HELLO]{}'.format(config['parent-id'])
        self.PBYE = '[BYE]{}'.format(config['parent-id'])
        self.PINF = '[INF]{}'.format(self.config['parent-id'])
        self.PCMD = '[CMD]{}'.format(self.config['parent-id'])

        # If this node is not server, connect to a parent broker.
        if self.config['type'] != 'server':
            self.log('Configuring connection to parent node.', level=1)
            self.parent = mqtt.Client()
            self.parent.on_connect = self.parent_on_connect
            self.parent.on_message = self.parent_on_message

        # Connecting to local broker.
        self.log('Configuring connection to child node.', level=1)
        self.child = mqtt.Client()
        self.child.on_connect = self.child_on_connect
        self.child.on_message = self.child_on_message

        # Descendants ID database
        self.des_of_child = Tree(self.config['id'])

        if self.config['type'] != 'server':
            self.parent.connect(self.config['parent-mqtt-broker/ip'],
                                self.config['parent-mqtt-broker/port'],
                                self.config['keep-alive'])
        self.child.connect(self.config['local-mqtt-broker/ip'],
                           self.config['local-mqtt-broker/port'],
                           self.config['keep-alive'])

        while True:
            if self.config['type'] != 'server':
                self.parent.loop()
            self.child.loop()

    def parent_on_connect(self, client, userdata, flags, rc):
        self.log('Publishing {} to {} and Subscribing {}'.format(self.PHELLO, self.get_configuration(), self.PCMD), 2)
        self.parent.publish(self.PHELLO, self.get_configuration(), qos=1)
        self.parent.subscribe(self.PCMD, qos=1)

    def parent_on_message(self, client, userdata, msg):
        self.log('Message received from parent. topic: {}, payload: {}'.format(msg.topic, msg.payload))
        # TODO if CMD tag is there, find proper child and publish it there.

    def child_on_connect(self, client, userdata, flags, rc):
        self.log('Subscribing {}, {}, {}'.format(self.HELLO, self.BYE, self.INF), level=2)
        self.child.subscribe(self.HELLO, qos=1)
        self.child.subscribe(self.BYE, qos=1)
        self.child.subscribe(self.INF, qos=1)

    def child_on_message(self, client, userdata, msg):
        topic, payload = msg.topic, fromjson(msg.payload.decode())
        self.log('Message received from child. topic: {}, payload: {}'.format(topic, payload))

        if topic == self.HELLO:
            self.child.publish(self.PHELLO, msg.payload)
            self.des_of_child.add(payload['pid'], payload['id'])
        elif topic == self.BYE:
            self.child.publish(self.PBYE, msg.payload)
            self.des_of_child.remove(payload['id'])
        elif topic == self.INF:
            self.child.publish(self.PINF, msg.payload)

        self.log("Descendants: {}".format(self.des_of_child), level=1)


if __name__ == '__main__':
    ######################## Single Server ##############################
    # Gateway(config={
    #     'id': 1,
    #     'group-id': 1,
    #     'type': 'server',
    #     'keep-alive': 60,
    #     'local-mqtt-broker/ip': 'localhost',
    #     'local-mqtt-broker/port': 1883,
    #
    #     'parent-id': 0,
    #     'parent-mqtt-broker/ip': 'localhost',
    #     'parent-mqtt-broker/port': 1883,
    # })

    ############################## 1 Server and 1 Gateway ##############################
    Thread(target=Gateway, args=[{
        'id': 1,
        'group-id': 1,
        'type': 'server',
        'keep-alive': 60,
        'local-mqtt-broker/ip': 'localhost',
        'local-mqtt-broker/port': 1883,

        'parent-id': 0,
        'parent-mqtt-broker/ip': 'localhost',
        'parent-mqtt-broker/port': 1883,
    }]).start()

    sleep(1)

    Gateway(config={
        'id': 2,
        'group-id': 2,
        'type': 'gateway',
        'keep-alive': 60,
        'local-mqtt-broker/ip': 'localhost',
        'local-mqtt-broker/port': 1883,

        'parent-id': 1,
        'parent-mqtt-broker/ip': 'localhost',
        'parent-mqtt-broker/port': 1883,
    })
