import socket
import subprocess

f = open("/tmp/testsound_client.wav", 'w')

cSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cSocket.connect(("localhost",2727))
cSocket.send("Hello world! test")
while True:
	buffer = cSocket.recv(1024)
	f.write(buffer)
	if len(buffer) < 1024:
		break
cSocket.close()
f.close()
subprocess.call(["aplay", "/tmp/testsound_client.wav"])
