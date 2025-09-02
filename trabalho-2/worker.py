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
    
    # Define o fuso horário de Brasília
    brasilia_tz = pytz.timezone('America/Sao_Paulo')
    
    # Cria um objeto datetime "aware" (consciente do fuso) em UTC a partir do timestamp
    utc_dt = datetime.fromtimestamp(timestamp, tz=pytz.utc)
    
    # Converte o tempo para o fuso horário de Brasília
    brasilia_dt = utc_dt.astimezone(brasilia_tz)
    
    # Formata a string no novo fuso
    return brasilia_dt.strftime("%H:%M:%S")


# Pode vir do docker-compose (env) ou ser sorteado
OFFSET = float(os.getenv("OFFSET", random.randint(-10, 10)))
local_time = time.time() + OFFSET

def handle_connection(conn, addr):
    global local_time
    data = conn.recv(1024).decode()
    if data == "TIME_REQUEST":
        conn.sendall(str(local_time).encode())
    elif data.startswith("ADJUST:"):
        adjustment = float(data.split(":")[1])
        local_time += adjustment
        print(f"[WORKER] Ajuste aplicado: {adjustment:.2f}s, novo tempo: {timestamp_to_local_time(local_time)}")
    conn.close()

def server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[WORKER] Aguardando conexões... (tempo inicial = {timestamp_to_local_time(local_time)})")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_connection, args=(conn, addr)).start()

if __name__ == "__main__":
    print(f"[WORKER] Tempo inicial (com offset {OFFSET}): {timestamp_to_local_time(local_time)}")
    server()
