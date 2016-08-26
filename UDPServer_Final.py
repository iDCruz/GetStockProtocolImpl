import socket
import os
import fileinput
import sys
import string

######################## Constant values to be used later ########################
#FILESTRING is the text file to save registered users to and read from           #
FILESTRING = "Users.txt"                                                         #
                                                                                 #
#IP is the IP string to be used when creating a socket for the server            #
IP = "192.168.1.137"                                                             #
                                                                                 #
#PORT is the port number to be used for the server                               #
PORT = 1050                                                                      #
                                                                                 #
#MESSAGES is the list of appropriate messages the receiver can send              #
MESSAGES =["REG", "UNR", "QUO"]                                                  #
                                                                                 #
#SERVERMSGS is the list of messages the server can send                          #
SERVERMSGS =["ROK", "INP", "UAE", "INC", "UNR", "INU"]                           #
##################################################################################

#DOCUMENTATION
#https://wiki.python.org/moin/UdpCommunication
#https://docs.python.org/3/
#http://stackoverflow.com/questions/17747522/how-to-delete-a-line-from-a-text-file-using-the-line-number-in-python

#Creates the Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#Binds the socket created to the IP and PORT specified above
sock.bind((IP, PORT))

#Receiver stays open while looping to receive messages from clients.
#If a message with proper commands is received sends proper message back to client.
while True:
    #File Creation/Handling for text file containing users
    userFile = open(FILESTRING, "w") if not os.path.isfile(FILESTRING) else open(FILESTRING, "r+")
    userFile.close()
    userFile = open(FILESTRING, "r+")#FILE READING AND APPENDING
    userList = userFile.read().split('\n')

    #Message list to be filled and converted to string to send to client later
    Message = []

    #Received message from client and address
    RecMessage, addr = sock.recvfrom(1024)
    RecMsgList = RecMessage.decode("ASCII").strip().split(",")
    for item in RecMsgList:
        RecMsgList[RecMsgList.index(item)] = item.strip()
    if not RecMsgList[-1].endswith(";"):
        Message.append("ERROR no ;") #DUBCHECK WITH CHRISTENSEN
    elif (RecMsgList[0]) not in MESSAGES:
        Message.append(SERVERMSGS[3])
    elif len(RecMsgList) < 2:
        Message.append(SERVERMSGS[1])
    else:
        RecMsgList[-1] = RecMsgList[-1].replace(";", "") #DUBCHECK
        RecMsgList[1] = RecMsgList[1].upper()
        ######Can use this line to remove wasted space by user sent messages
        #[RecMsgList.remove(item) for item in RecMsgList if item.isspace()]
        #prints to screen the received message from client and client address/port
        print ("Received Message: " + ",".join(RecMsgList))
        print (addr)

        #Adds ROK to message to send if a proper command is sent and the user is in the list from the users file or is being registered
        #else sends "ERR"
        if RecMsgList[0] in MESSAGES:
            if RecMsgList[0] == MESSAGES[0] or RecMsgList[0] == MESSAGES[1]:
                if len(RecMsgList) != 2: #Check number of parameters for REG and UNR
                    Message.append(SERVERMSGS[1])

                #Register
                elif RecMsgList[0] == MESSAGES[0]:
                    usernameValid = True
                    for item in RecMsgList[1]:
                        if item not in string.ascii_letters and item not in string.digits: #Username is invalid if character non-ASCII (space is non-ASCII)
                            usernameValid = False
                            break
                    if usernameValid == False or len(RecMsgList[1]) > 32: #Check username length
                        Message.append(SERVERMSGS[5])
                    elif RecMsgList[1] in userList: #if username is registered sends UAE
                        Message.append(SERVERMSGS[2])
                    else:                           #else registers user
                        userFile.write(RecMsgList[1] + '\n')
                        Message.append(SERVERMSGS[0])
                
                #Unregister
                elif RecMsgList[0] == MESSAGES[1]:
                    userFile.close()
                    if RecMsgList[1] not in userList: #if username not registered sends UNR
                        Message.append(SERVERMSGS[4])
                    else:                             #else deletes user
                        #http://stackoverflow.com/questions/17747522/how-to-delete-a-line-from-a-text-file-using-the-line-number-in-python
                        for line in fileinput.input(FILESTRING,inplace = True):
                            if RecMsgList[1] not in line:
                                sys.stdout.write(line)
                        Message.append(SERVERMSGS[0])
                        fileinput.close()
                        userList.remove(RecMsgList[1])
            else:
                for item in RecMsgList:     #Checks for white space paramaters. If there is one, this returns temp var x as true.
                    x = True if item.isspace() else False
                    if x == True:
                        break
                    
                usernameValid = True
                for item in RecMsgList[1]:
                    if item not in string.ascii_letters and item not in string.digits: #Username is invalid if character non-ASCII (space is non-ASCII)
                        usernameValid = False
                        break
                    
                if len(RecMsgList) < 3 or x == True :   #Checks for validity of number of parameters and white space parameters. Sends INP if any white space parameters or not enough parameters.
                    Message.append(SERVERMSGS[1])
                elif usernameValid == False or len(RecMsgList[1]) > 32: #added for invalid username
                    Message.append(SERVERMSGS[5])
                elif RecMsgList[1] in userList:
                    for item in RecMsgList[2:]:
                        RecMsgList[RecMsgList.index(item)]= item.upper()
                    Message.append(SERVERMSGS[0])
                    #check stock text file for parameters
                    quotes = {}
                    myFile = open("stockfile.txt") #could introduce more checking with file exists
                    for x in myFile:
                        y = x.split(" ")
                        quotes.update({y[0]:y[1]})
                        print (str(quotes))
                    #if stock quo not in file return -1
                    for item in RecMsgList[2:]:
                        if item in quotes.keys():
                            Message.append(str(quotes[item]))
                        else:
                            Message.append(str(-1))
                else:
                    Message.append(SERVERMSGS[4])
        else:
            Message.append(SERVERMSGS[3])
        userFile.close()
        #Adds list of stocks (eventually) if the command is QUO and the conditional statement above appends "ROK" and not "ERR"
        #Message.append(",Stocks List Here") if MESSAGES[2] == RecMsgList[0] and Message != SERVERMSGS[3] else Message.append("")

    #Sends message to client
    sock.sendto(bytes(Message[0] + ";", "ASCII"), addr) if len(Message) == 1 else sock.sendto(bytes(",".join(Message) + ";", "ASCII"), (addr))
