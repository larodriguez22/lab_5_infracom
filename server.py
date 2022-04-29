# https://gist.github.com/AlyoshaS/ecd9aa68a5358b467a70cf39aa681c00

# Importar la libreria del socket
import socket
import threading
import hashlib
import os
import time
from datetime import datetime
FORMAT = "utf-8"
FILE_END = "FILE_END"
PORT = 12345

def main():
    # Modificar direccion del servidor
    host = "localhost" #"192.168.85.1" #"192.168.85.1"  # "192.168.1.2" #Server address #Tomas: 192.168.85.1
    port = PORT

    # socket.AF_INET define la familia de protocolos IPv4. Socket.SOCK_DGRAM define la conexión UDP.
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # La instrucción s.bindhost, port toma solo un argumento. Vincule el socket al host y al número de puerto.
    # La sentencia s.listen(2) escucha la conexión y espera al cliente.
    s.bind((host, port)) #bind server

    # El ciclo while mantiene vivo el programa del servidor y no detiene la ejecución del código. 
    # Puede establecer un límite de conexión para el ciclo while; 
    # Por ejemplo, establezca while i > 10 e incremente 1 en i(i += 1) en cada conexión.

    # Se pide la informacion del archivo que se desea enviar al usuario
    # 1 identifica al archivo de 100MB y 2 identifica al archivo de 250MB
    # Una vez se identifica la informacion, se abre el archivo correspondiente

    print("Server config:")

    selected_file = int(input("Escriba el id del archivo que quiere enviar, donde 1 es para el archivo de 100MB "
                        "y 2 es para el archivo de 250MB: "))

    concurrent_clients = int(input("Escriba el número de conexiones concurrentes que desea tener: "))

    packet_size = int(input("Escriba el tamaño de los paquetes a enviar en KB, de 1 a 64: "))
    packet_size *= 1000
    # s.listen(concurrent_clients)

    print("Server listening on port ", PORT)

    current_clients = 0
    barrier = threading.Barrier(concurrent_clients)
    while concurrent_clients > current_clients:

        message, address = s.recvfrom(4096)

        print("Accepted {} connections so far".format(current_clients))

        thread = UdpServerThread(current_clients, message, address, selected_file, barrier, packet_size, s)
        thread.start()

        current_clients += 1

def on_new_client(message, address, selected_file, barrier, packet_size, s):
    barrier.wait()
    t1 = time.time()
    print("Enviando archivo al usuario", address)
    if selected_file == 1:
        path = "data/100MB.txt"
    elif selected_file == 2:
        path = "data/250MB.txt"
    else:
        print("No se pudo leer el archivo")
        path = open("/")

    # Se lee el archivo
    # breakpoint()
    file = open(path, "r")
    # data = file.read()

    file_size = os.path.getsize(path)
    fz = str(file_size)
    # Envio cuatro cosas
    # La función conn.send() envía el mensaje al cliente. 
    # 1. La informacion del tamaño del archivo
    s.sendto(fz.encode(FORMAT), address)
    # El archivo dividido en paquetes de de tamaño packet_size
    send_bytes = 0
    packets = 0
    print("packet_size {} KB".format(packet_size/1000))
    while True:
        file = open(path, "rb")
        file_content = file.read(packet_size)
        while file_content:
            # 2. El (file_content)
            s.sendto(file_content, address)
            send_bytes += len(file_content)
            file_content = file.read(packet_size)
            packets += 1
        break
    print("Archivo enviado correctamente en {} particiones".format(packets))
    # 4. Un mensaje de confirmación de que termino de enviar correctamente
    s.sendto(b"Termino:200", address)

    # Recibo un mensaje de confirmacion de que llego el archivo completo y correctamente
    recibido = s.recv(packet_size)
    t2 = time.time()

    date = datetime.now()
    date_time = date.strftime("%m-%d-%Y-%H-%M-%S")
    text = "---------------------\n"
    text += "Nombre archivo: " + path + "\n"
    text += "Tamaño del archivo: " + str(file_size) + " Bytes" + "\n"
    text += "Conectado con el cliente: " + str(address) + "\n"
    text += "El tiempo de transferencia es: " + str(t2 - t1) + " ms""\n"
    print(text)
    with open('logs_servidor/' + date_time + "-log.txt", 'a') as f:
        f.write(text)

class UdpServerThread(threading.Thread):
    def __init__(self, thread_id, message, address, selected_file, barrier, packet_size, s):
        threading.Thread.__init__(self)
        self.thread_ID = thread_id
        self.message = message
        self.address = address
        self.selected_file = selected_file
        self.barrier = barrier
        self.packet_size = packet_size
        self.socket = s

    def run(self):
        on_new_client(self.message, self.address, self.selected_file, self.barrier, self.packet_size, self.socket)

if __name__ == "__main__":    
    main()