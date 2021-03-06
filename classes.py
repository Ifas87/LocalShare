import threading, pickle, socket, time, os
from tkinter.messagebox import askyesno
from cryptography.fernet import Fernet

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 1024 * 4

"""
An Encapsulating class used to store boolean flags.
These flags help denote the status of the connection and progress.

The flags represent 'Available?', 'confirmation' , 'About to Send', 'busy'
'encrypted' and 'compressed' respectively
"""
class pingMessage():
    flags = [False, False, False, False, False, False]
    filename = ""
    key = None
    def __init__(self, flags):
        self.flags = flags

    def getFlags(self):
        return self.flags

    def setFilename(self, filename):
        self.filename=filename

    def getFilename(self):
        return self.filename

    def setKey(self, key):
        self.key=key

    def getKey(self):
        return self.key

"""

"""
class address():
    def __init__(self, name, addr):
        self.name = name
        self.addr = addr

    def getName(self):
        return self.name

    def getAddr(self):
        return self.addr

    def print(self):
        return [self.name, self.addr]
    

"""

"""
class probingThread(threading.Thread):
    def __init__(self, device, viable_devices, port):
        threading.Thread.__init__(self)

        self.probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = port
        self.device = device
        self.viable_devices = viable_devices
        self.probe.settimeout(5)
        
    def run(self):
        print("candidate", self.device.print())
        try:
            self.probe.connect((self.device.getAddr(), self.port))
            self.probe.send(pickle.dumps(pingMessage([True, False, False, False, False, False])))

            response = pickle.loads(self.probe.recv(BUFFER_SIZE))
            print(response.getFlags())
            if (response.getFlags()[1] == True):
                self.probe.shutdown(socket.SHUT_RDWR)
                self.probe.close()
                self.viable_devices.append(self.device)
            else:
                self.probe.shutdown(socket.SHUT_RDWR)
                self.probe.close()

        except:
            pass
            
        """            
        except (socket.error, ConnectionRefusedError, OSError, WindowsError) as exc:
            if exc.winerror == 10057:
                print("Special Error")
            print(exc)
            self.probe.shutdown(socket.SHUT_RDWR)
            self.probe.close()
        """
        
        
class beaconThread(threading.Thread):
    def __init__(self, host, port):
        threading.Thread.__init__(self)

        self.beacon = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.beacon.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.beacon.bind((host, port))
        
    def run(self):
        self.beacon.listen(10)
        while(True):
            clientsock, clientAddress = self.beacon.accept()

            csocket = clientsock
            dataFromClient = pickle.loads(clientsock.recv(BUFFER_SIZE))

            if (dataFromClient.getFlags())[0] == True:
                message = pickle.dumps(pingMessage([False, True, False, False, False, False]))

            csocket.send(message)


"""
    Classes for managing sockets separately as each server socket would
    block other programs from executing
"""
class receivingThread(threading.Thread):
    """
    initialising section for the socket and the thread
    """
    def __init__(self, host, port):
        threading.Thread.__init__(self)
        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))

        self.filename = ""

    """
    Specific instructions function
    """
    def run(self):
        self.server.listen(10)
        while(True):
            clientsock, clientAddress = self.server.accept()

            csocket = clientsock
            dataFromClient = pickle.loads(clientsock.recv(BUFFER_SIZE))

            if (dataFromClient.getFlags())[0] == True:
               message = pickle.dumps(pingMessage([False, True, False, False, False, False]))

            csocket.send(message)

            received = csocket.recv(BUFFER_SIZE).decode()
            self.filename, self.filesize = received.split(SEPARATOR)
            
            self.filename = "stuff" + os.path.basename(self.filename)
            self.filesize = int(self.filesize)

            with open(self.filename, "wb") as f:
                while(True):
                    print("About to loop into", self.filename)
                    bytes_read = csocket.recv(BUFFER_SIZE)
                    if not bytes_read:
                        break
                    f.write(bytes_read)
            
            print("File received")
            time.sleep(1)
        print("done")


"""
The same class but for the client/sending thread
"""
class sendingThread(threading.Thread):
    def __init__(self, host, port, filename, Encryption, Compression, key):
        threading.Thread.__init__(self)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.message = pingMessage([False, False, True, False, Encryption, Compression])

        self.host = host
        self.port = port
        self.filename = filename
        self.filesize = os.path.getsize(filename)
        self.key = key
        self.fern = Fernet(self.key)
        
    def run(self):
        self.client.connect((self.host, self.port))
        self.message.setFilename(self.filename)
        self.message.setKey(self.key)
        self.message = pickle.dumps(self.message)
        
        self.client.send(self.message)
        dataFromServer = self.client.recv(1024)

        if (pickle.loads(dataFromServer).getFlags())[1] == True:
            #self.client.send(f"{self.filename}{SEPARATOR}{self.filesize}".encode())
            
            print("sent filename by client ")
            
            with open(self.filename, "rb") as f:
                if((pickle.loads(self.message).getFlags())[4] == True):
                    bytes_read = f.read()
                    encrypted_data = self.fern.encrypt(bytes_read)
                    self.client.sendall(encrypted_data)
                else:
                    while True:
                        bytes_read = f.read(BUFFER_SIZE)
                        if not bytes_read:
                            break
                        self.client.sendall(bytes_read)

        print("File sent")
        self.client.shutdown(socket.SHUT_RDWR)
        self.client.close()


"""
The flags represent 'Available?' , 'confirmation' , 'About to Send', 'busy'
'encrypted' and 'compressed' respectively
"""
class receivingThread2(threading.Thread):
    """
    initialising section for the socket and the thread
    """
    def __init__(self, host, port):
        threading.Thread.__init__(self)
        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))

        self.filename = ""
        self.key = None
        self.enc_module = None

    """
    Specific instructions function
    """
    def run(self):
        self.server.listen(10)
        while(True):
            clientsock, clientAddress = self.server.accept()

            csocket = clientsock
            dataFromClient = pickle.loads(clientsock.recv(BUFFER_SIZE))
            print(dataFromClient.getFlags())

            if (dataFromClient.getFlags())[2] == True:
                reply = pickle.dumps(pingMessage([False, True, False, False, False, False]))
                csocket.send(reply)

                self.key = dataFromClient.getKey()
                self.enc_module = Fernet(self.key)
                
                popup = "User has sent the following file: " + dataFromClient.getFilename() + "\n Accept file download?"
                user_response = askyesno(title="Incoming File Sent", message=popup)

                self.filename = "stuff" + os.path.basename(dataFromClient.getFilename())
                
                if user_response:
                    with open(self.filename, "wb") as f:
                        total_bytes = b'' 
                        if (dataFromClient.getFlags())[4] == True:
                            while(True):
                                bytes_read = csocket.recv(BUFFER_SIZE)
                                if not bytes_read:
                                    break
                                total_bytes += bytes_read
                            f.write(self.enc_module.decrypt(total_bytes))
                        else:
                            while(True):
                                bytes_read = csocket.recv(BUFFER_SIZE)
                                if not bytes_read:
                                    break
                                f.write(bytes_read)
            
            print("File received")
            time.sleep(1)
        print("done")


"""
newServer = receivingThread2("127.0.0.1", 9090)
newServer.start()

newclient = sendingThread("127.0.0.1", 9090, "hello.txt")
newclient.start()
"""
