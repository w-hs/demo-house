#!/usr/bin/python
import signal
import json
import subprocess
import SocketServer
import SimpleHTTPServer

# Json Keys definieren
ZIGBEE 	= "zigbee"
ZWAVE 	= "zwave"
ENOCEAN = "enocean"

# leere Dictionaries anlegen
device_ids = {}
# Device Id's anlegen 
device_ids["10c4:ea60"] = ZWAVE
device_ids["0451:16a8"] = ZIGBEE
device_ids["0403:6001"] = ENOCEAN

# per lsusb alle usb device ids erfragen / vergleichen und json bauen
def check_device_ids(device_ids):
	devices_found = {}
	for device in device_ids.values():
		devices_found[device] = "false"

	# lsusb Ausgabe checken
	df = subprocess.check_output("lsusb", shell=True)
	# Zeilenweise auswerten
	for line in df.split('\n'):
		if line:
			# Spalte 6 aus lsusb lesen
			device_id = line.split(' ')[5]
			if device_id in device_ids:
				devices_found[device_ids[device_id]] = "true"
	return devices_found

def signal_handler(signal, frame):
	print('You pressed Ctrl+C! Bye...')
	sys.exit(0)

# do_GET() des HTTPHanlders ueberschreiben
class CustomHTTPHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	def end_headers(self):
		self.send_header('Access-Control-Allow-Origin', '*')
		SimpleHTTPServer.SimpleHTTPRequestHandler.end_headers(self)
	
	def do_GET(self):
		devs = check_device_ids(device_ids)
		devs = json.dumps(devs)
		self.wfile.write("callback(" + devs + ");")
		return

if __name__ == "__main__":
	# Signal-Handler registrieren
	signal.signal(signal.SIGINT, signal_handler)

	# HTTP-Server starten der Json liefert
	handler = CustomHTTPHandler
	server = SocketServer.TCPServer(("",9999), handler)
	print "Searching for this device id's"
	print device_ids
	try:
		server.serve_forever()
	except:
		pass
	server.server_close()
