import os
import random
import socket
import threading
import time
from datetime import datetime
import pytz

HOST = "0.0.0.0"
PORT = 5000

def timestamp_to_local_time(timestamp):
    """Converte timestamp Unix para horário local de Brasília no formato hh:mm:ss"""
    brasilia_tz = pytz.timezone('America/Sao_Paulo')
    utc_dt = datetime.fromtimestamp(timestamp, tz=pytz.utc)
    brasilia_dt = utc_dt.astimezone(brasilia_tz)
    return brasilia_dt.strftime("%H:%M:%S")

# O valor inicial do desvio é definido pelo Docker Compose ou sorteado.
time_offset = float(os.getenv("OFFSET", random.randint(-10, 10)))

def handle_connection(conn, addr):
    global time_offset
    
    data = conn.recv(1024).decode()

    if data == "TIME_REQUEST":
        # Ele é o tempo real do sistema + o nosso desvio atual.
        current_worker_time = time.time() + time_offset
        conn.sendall(str(current_worker_time).encode())

    elif data.startswith("ADJUST:"):
        adjustment = float(data.split(":")[1])
        
        time_offset += adjustment
        
        # Para o log, calculamos o novo tempo atual para exibi-lo.
        new_time = time.time() + time_offset
        print(f"[WORKER] Ajuste de {adjustment:.4f}s aplicado ao offset. Novo tempo: {timestamp_to_local_time(new_time)}")
        
    conn.close()

def server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        initial_time = time.time() + time_offset
        print(f"[WORKER] Aguardando conexões... (tempo inicial = {timestamp_to_local_time(initial_time)})")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_connection, args=(conn, addr)).start()

if __name__ == "__main__":
    initial_time = time.time() + time_offset
    print(f"[WORKER] Tempo inicial (com offset {time_offset:.2f}s): {timestamp_to_local_time(initial_time)}")
    server()