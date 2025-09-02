import os
import socket
import statistics
import time
from datetime import datetime
import pytz

HOST = "0.0.0.0"
PORT = 5000
WORKERS = ["worker1", "worker2"]
# Pega o intervalo do ambiente, com um padrão de 10s
SYNC_INTERVAL = int(os.getenv("SYNC_INTERVAL", 10))

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


def get_worker_time_with_rtt(worker):
    """
    Solicita o tempo de um worker e estima a latência da rede (RTT).
    Retorna o tempo do worker ajustado pela latência e o tempo de diferença.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)  # Timeout de 2 segundos para evitar travamentos
            
            # 1. Anota o tempo antes de enviar
            time_before_request = time.time()
            
            s.connect((worker, PORT))
            s.sendall(b"TIME_REQUEST")
            data = s.recv(1024).decode()
            
            # 2. Anota o tempo depois de receber a resposta
            time_after_response = time.time()

            worker_time = float(data)
            
            # 3. Calcula o RTT e o ajuste
            rtt = time_after_response - time_before_request
            latency_adjustment = rtt / 2
            
            # O tempo estimado do worker no momento da resposta do master é o tempo que ele enviou + metade do RTT
            estimated_worker_time = worker_time + latency_adjustment
            
            print(f"[MASTER] Recebi tempo de {worker}: {timestamp_to_local_time(worker_time)} (RTT: {rtt:.4f}s)")
            
            return estimated_worker_time

    except (socket.error, socket.timeout) as e:
        print(f"[MASTER] Erro ao conectar com {worker}: {e}")
        return None

def send_adjustment(worker, adjustment):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect((worker, PORT))
            s.sendall(f"ADJUST:{adjustment}".encode())
    except (socket.error, socket.timeout) as e:
        print(f"[MASTER] Erro ao enviar ajuste para {worker}: {e}")

def main():
    print(">>> Master iniciado")
    while True:
        print("\n" + "="*40)
        print(f"[MASTER] Iniciando novo ciclo de sincronização em {timestamp_to_local_time(time.time())}")
        
        local_time = time.time()
        print(f"[MASTER] Tempo local: {timestamp_to_local_time(local_time)}")

        worker_times = {} # Usar um dicionário para manter a associação worker -> tempo
        for w in WORKERS:
            wt = get_worker_time_with_rtt(w)
            if wt is not None:
                worker_times[w] = wt

        if not worker_times:
            print("[MASTER] Nenhum worker respondeu. Tentando novamente em breve.")
            time.sleep(SYNC_INTERVAL)
            continue
            
        # Inclui o tempo do master no cálculo
        all_times = [local_time] + list(worker_times.values())
        avg_time = statistics.mean(all_times)
        print(f"[MASTER] Média calculada (com ajuste de RTT): {timestamp_to_local_time(avg_time)}")

        # Envia ajustes para o master (apenas para exibição)
        master_adjustment = avg_time - local_time
        print(f"[MASTER] Ajuste para o próprio master: {master_adjustment:.4f}s (não aplicado, apenas referência)")

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