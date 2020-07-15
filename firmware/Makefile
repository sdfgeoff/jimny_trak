PORT = /dev/ttyACM0

AMPY = ampy
ESPTOOL = esptool.py

load:
	$(AMPY) -p $(PORT) -b 115200 put main.py
	$(AMPY) -p $(PORT) -b 115200 put webpage.py
	$(AMPY) -p $(PORT) -b 115200 put vehicle.py
	$(AMPY) -p $(PORT) -b 115200 put index.html


flash:
	$(ESPTOOL) --port $(PORT) --baud 115200 write_flash 0 esp8266-20191220-v1.12.bin

monitor:
	miniterm2.py $(PORT)  115200 --raw
