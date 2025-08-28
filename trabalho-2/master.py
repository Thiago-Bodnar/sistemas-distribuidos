import socket
import statistics
import time
from datetime import datetime

HOST = "0.0.0.0"
PORT = 5000
WORKERS = ["worker1", "worker2"]  # nomes dos containers no docker-compose

def timestamp_to_local_time(timestamp):
    """Converte timestamp Unix para horário local no formato hh:mm:ss"""
    return datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")

def get_worker_time(worker):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((worker, PORT))
        s.sendall(b"TIME_REQUEST")
        data = s.recv(1024).decode()
        return float(data)

def send_adjustment(worker, adjustment):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((worker, PORT))
        s.sendall(f"ADJUST:{adjustment}".encode())

def main():
    print(">>> Master iniciado")
    local_time = time.time()
    print(f"[MASTER] Tempo local: {timestamp_to_local_time(local_time)}")

    worker_times = []
    for w in WORKERS:
        wt = get_worker_time(w)
        print(f"[MASTER] Recebi tempo de {w}: {timestamp_to_local_time(wt)}")
        worker_times.append(wt)

    # inclui o tempo do master no cálculo
    all_times = [local_time] + worker_times
    avg_time = statistics.mean(all_times)
    print(f"[MASTER] Média calculada: {timestamp_to_local_time(avg_time)}")

    # envia ajustes
    for w, wt in zip(WORKERS, worker_times):
        adjustment = avg_time - wt
        send_adjustment(w, adjustment)
        print(f"[MASTER] Ajuste enviado a {w}: {adjustment:.2f}s")

    print("[MASTER] Sincronização concluída!")

if __name__ == "__main__":
    main()
