import socket

IP = "192.168.1.137"
PORT = 1050

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(5)
while 1:
    MESSAGE = input("Enter Command: ")

    print ("Message to send: " + MESSAGE)

    count = 1
    sock.sendto(bytes(MESSAGE, "ASCII"), (IP,PORT))
    while 1:
        try:
            newmessage, address = sock.recvfrom(1024)
            print(address)
            print(newmessage.decode("ASCII"))
            break
        except socket.timeout:
            if (count < 3):
                sock.sendto(bytes(MESSAGE, "ASCII"), (IP,PORT))
                count +=1
            else:
                print (str(count) +"rd try")
                break
