import socket
import sys
import os
import threading
import msvcrt

class ServerThread(threading.Thread): #handles server input asynchronously from client input
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = 1
    def run(self):
        while self.running == True:
            if msvcrt.kbhit():
                terminal = input()
                server_message_str = '[Server] ' + terminal + '\n' #prefix with "server:" and newline for client
                server_message = server_message_str.encode() #convert to bytes for sending
                if terminal == 'exit':
                    print('[!] Shutting down server')
                    os._exit(0) #kills the program and returns to command line                    
                elif terminal.startswith('~'): #send to a specific client
                    clientid = int(terminal[1])-1 #second character of string is client id
                    #this code will only handle <10 clients
                    try:
                        client = threads[clientid]
                        if client.running == True:
                            client.client.sendall(server_message)
                        else: #old inactive thread
                            print('[!] Cannot send - not an active client ID')
                    except IndexError: #not a valid client id
                        print('[!] Cannot send - not a valid client ID')                        
                else: #broadcast message to all connected clients if no ~ prefix
                    #check if there are any active client threads
                    if any(t.running == True for t in threads):
                        for clients in threads:
                            if clients.running == True: #check to make sure thread is not
                                #associated with disconnected client
                                #alternatively could remove old threads from the array 
                                clients.client.sendall(server_message)
                    else: #no active client threads
                        print('[!] Cannot send - no active clients')

class ClientThread(threading.Thread):
    def __init__(self, clientobject, threadnum):
        threading.Thread.__init__(self)
        self.running = 1
        self.client = clientobject
        self.clientid = threadnum
    def run(self):
        while self.running == True:
            try:
                client_message = self.client.recv(1024)
                if(client_message):
                    print('[Client {}] {}'.format(self.clientid, client_message.decode().rstrip('\n')))
                    if (client_message == b'~q\n'): #graceful disconnect from server
                        print('[!] Client {} disconnected'.format(self.clientid))
                        self.client.close()
                        self.running = 0
            except (ConnectionError, TimeoutError): #recv returns error; assume client disconnected
                print('[!] Client {} disconnected'.format(self.clientid))
                self.client.close()
                self.running = 0 #mark thread as stopped

hostname, aliaslist, ipaddrlist = socket.gethostbyname_ex(socket.gethostname())
ipaddr = ipaddrlist[0]
portnum = 31337
threadnum = 1 #client thread number/ID
threads = [] #array of client threads

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('[!] Starting up on', ipaddr, 'port', portnum)
sock.bind(('', portnum)) #bind to all interfaces -internal and external
print('[!] Server ready. Waiting for a connection.')

while True:
    sock.listen(5)

    server = ServerThread()
    server.start()
    
    client, client_address = sock.accept()
    print('[+] Connection from', client_address, ': Client ', threadnum)
    #Send confirmation message to client
    client.sendall(b'Connected to server. Type ~q to disconnect.\n')

    #create new thread for client
    newthread = ClientThread(client, threadnum)
    newthread.start()
    threads.append(newthread)
    threadnum += 1
                    
#if __name__ == "__main__":
#    main()
