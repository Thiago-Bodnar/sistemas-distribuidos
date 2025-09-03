import os
import socket
import statistics
import time
from datetime import datetime
import pytz

HOST = "0.0.0.0"
PORT = 5000
WORKERS = ["worker1", "worker2"]
SYNC_INTERVAL = int(os.getenv("SYNC_INTERVAL", 10))

# O master começa perfeitamente sincronizado (offset = 0).
master_time_offset = 0.0

def timestamp_to_local_time(timestamp):
    """Converte timestamp Unix para horário local de Brasília no formato hh:mm:ss"""
    brasilia_tz = pytz.timezone('America/Sao_Paulo')
    utc_dt = datetime.fromtimestamp(timestamp, tz=pytz.utc)
    brasilia_dt = utc_dt.astimezone(brasilia_tz)
    return brasilia_dt.strftime("%H:%M:%S")

def get_worker_time_with_rtt(worker):
    """Solicita o tempo de um worker e estima a latência da rede (RTT)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            time_before_request = time.time()

            s.connect((worker, PORT))
            s.sendall(b"TIME_REQUEST")
            data = s.recv(1024).decode()
            time_after_response = time.time()

            worker_time = float(data)

            rtt = time_after_response - time_before_request
            latency_adjustment = rtt / 2

            estimated_worker_time = worker_time + latency_adjustment
            print(f"[MASTER] Recebi tempo de {worker}: {timestamp_to_local_time(worker_time)} (RTT: {rtt:.4f}s)")
            return estimated_worker_time
    except (socket.error, socket.timeout) as e:
        print(f"[MASTER] Erro ao conectar com {worker}: {e}")
        return None

def send_adjustment(worker, adjustment):
    """Envia o valor de ajuste para um worker."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect((worker, PORT))
            s.sendall(f"ADJUST:{adjustment}".encode())
    except (socket.error, socket.timeout) as e:
        print(f"[MASTER] Erro ao enviar ajuste para {worker}: {e}")

def main():
    global master_time_offset
    
    print(">>> Master iniciado")
    while True:
        # A mensagem de início de ciclo agora também usa o tempo ajustado do master.
        current_master_time_for_log = time.time() + master_time_offset
        print("\n" + "="*40)
        print(f"[MASTER] Iniciando novo ciclo de sincronização em {timestamp_to_local_time(current_master_time_for_log)}")
        
        local_time = time.time() + master_time_offset
        print(f"[MASTER] Tempo local do master: {timestamp_to_local_time(local_time)}")

        worker_times = {}
        for w in WORKERS:
            wt = get_worker_time_with_rtt(w)
            if wt is not None:
                worker_times[w] = wt

        if not worker_times:
            print("[MASTER] Nenhum worker respondeu. Tentando novamente em breve.")
            time.sleep(SYNC_INTERVAL)
            continue
            
        all_times = [local_time] + list(worker_times.values())
        avg_time = statistics.mean(all_times)
        print(f"[MASTER] Média calculada (com ajuste de RTT): {timestamp_to_local_time(avg_time)}")

        master_adjustment = avg_time - local_time
        master_time_offset += master_adjustment
        
        # O novo tempo do master é, por definição, a própria média que foi calculada.
        print(f"[MASTER] Ajuste aplicado ao próprio master: {master_adjustment:.4f}s. Novo tempo: {timestamp_to_local_time(avg_time)}")

        # Envia ajustes para os workers
        for w, wt in worker_times.items():
            adjustment = avg_time - wt
            send_adjustment(w, adjustment)
            print(f"[MASTER] Ajuste enviado a {w}: {adjustment:.4f}s")

        print("[MASTER] Sincronização concluída!")
        print(f"[MASTER] Aguardando {SYNC_INTERVAL} segundos para o próximo ciclo...")
        time.sleep(SYNC_INTERVAL)

if __name__ == "__main__":
    main()