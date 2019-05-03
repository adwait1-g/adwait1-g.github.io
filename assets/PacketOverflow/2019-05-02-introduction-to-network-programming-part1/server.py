#!/usr/bin/python3

import sys
import socket

# Server function
def server(ServerIPAddress, ServerPortNumber) : 

    # Server's IPAddress and PortNumber
    ServerPair = (ServerIPAddress, ServerPortNumber)

    # Create a listening socket
    ListenSocket = socket.socket()

    # Bind the listening socket to that pair
    ListenSocket.bind(ServerPair)

    RequestQueueLength = 1
    
    # Execute "listen" function
    ListenSocket.listen(RequestQueueLength)
    print("Server listening at ", ServerPair)

    # If a connection request comes in, accept that request by executing the accept function
    ClientHandleSocket, ClientPair = ListenSocket.accept()
    print("Connected to client at ", ClientPair)

    # Receive data sent by Client
    ClientData = ClientHandleSocket.recv(10000)
    ClientData = ClientData.decode('utf-8')

    print("Client: ", ClientData)
    
    SendData = "Hey Client! This is the Server. I have successfully recieved your message."
    SendData = bytes(SendData.encode('utf-8'))
    ClientHandleSocket.send(SendData)
    print("Data sent back to client")

    # Send Server data
    ClientHandleSocket.send(SendData)

    # Close the socket handling the client 
    ClientHandleSocket.close()
    print("Connection closed with client at ", ClientPair)

    # Close the listening socket (Usually, this is not done)
    ListenSocket.close()
    print("Server terminated!")


if __name__ == "__main__" : 

    if len(sys.argv) != 3 : 
        print("Usage: $ ", sys.argv[0], " <ServerIPAddress> <ServerPortNumber>")
        sys.exit()

    ServerIPAddress = sys.argv[1]
    ServerPortNumber = int(sys.argv[2])

    # Call the function
    server(ServerIPAddress, ServerPortNumber)
