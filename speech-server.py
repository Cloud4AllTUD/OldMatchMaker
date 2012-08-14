import socket
import subprocess

while True:
	mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	mySocket.bind(('', 2727))
	mySocket.listen(1)
	conn, addr = mySocket.accept()
	print 'Connected with ', addr
	while True:
		try:
			data = conn.recv(1024)
		except socket.error:
			break
		print data
		print "input length = ", len(data)
#		rc = subprocess.call(["espeak", "-w", "/tmp/command.wav", data])
#		f = open("/tmp/command.wav","r")
		buffer = subprocess.check_output(["espeak", "--stdout", data])
		print "buffer length: ", len(buffer)
		if not data:
			break
		conn.send(buffer)
	conn.close()
