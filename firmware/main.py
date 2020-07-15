""" Control over a vehicle with two tracks """
import time
import machine
import network
import socket

import vehicle
import webpage
import json



def host_network(name):
    sta_if = network.WLAN(network.AP_IF)
    sta_if.active(True)
    sta_if.config(essid=name)
    sta_if.config(authmode=0)  # 0 = open network



def create_webpage(port, vehicle):
    server = webpage.ControlWebpage(port)

    index = webpage.file_responder_factory("index.html")
    server.register_get_handler(
        b'/index.html',
        index
    )
    server.register_get_handler(b'/', index)


    def control_vehicle(data):
        try:
            raw_data = json.loads(data.decode('utf-8'))
        except:
            return (webpage.ERR_200, "Json decode error")

        speed = raw_data.get('s')
        turn = raw_data.get('t')
        lights = raw_data.get('l')

        print("before", speed, turn)

        
        if not isinstance(speed, int) or speed < -100 or speed > 100:
            speed = 0
        if not isinstance(turn, int) or turn < -100 or turn > 100:
            turn = 0
        if not isinstance(lights, bool):
            lights = False
        
        vehicle.set_speed(speed / 100, turn / 100)
        vehicle.set_lights(lights)

        telem_dict = {
            'b': vehicle.get_battery()
        }
        
        return (webpage.OK_200, json.dumps(telem_dict).encode('utf-8'))

    server.register_post_handler(b'/control', control_vehicle)
    

    return server


if __name__ == "__main__":
    VEHICLE = vehicle.get_vehicle()
    host_network("tiny_trak")

    WEBPAGE = create_webpage(80, VEHICLE)

    while(True):
        WEBPAGE.update()

