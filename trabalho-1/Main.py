from time import sleep
from threading import Thread, Lock
from random import randint, choice
from Thread import Processo

threads = []
threads_lock = Lock()

def get_ids():
    with threads_lock:
        return [t.id for t in threads]

def adicionar_thread(proc):
    with threads_lock:
        threads.append(proc)

def remover_thread(proc):
    with threads_lock:
        if proc in threads:
            threads.remove(proc)

def get_coordenador():
    with threads_lock:
        for t in threads:
            if t.isCoordenador:
                return t
    return None


def escolher_coordenador():
    with threads_lock:
        if not threads:
            return
        for t in threads:
            t.isCoordenador = False
        novo = choice(threads)
        novo.set_as_coordenador()
        print(f"[MAIN] Novo coordenador: {novo.id}")

def criar_processos():
    while True:
        sleep(40) 
        pid = randint(0, 10000)
        # garante ID único
        while pid in get_ids():
            print(f"[MAIN] ID {pid} já existia; sorteando outro.")
            pid = randint(0, 10000)

        p = Processo(pid, threads, threads_lock)
        adicionar_thread(p)
        p.start()
        print(f"[MAIN] Processo {pid} iniciado.")

        if get_coordenador() is None:
            escolher_coordenador()

def inativar_coordenador():
    while True:
        sleep(60)  
        coord = get_coordenador()
        if coord is not None:
            print(f"[MAIN] Coordenador {coord.id} morreu.")
            matar_processo(coord)
            # escolhe novo coordenador aleatório (fila antiga já morreu)
            if threads:
                escolher_coordenador()
        else:
            print("[MAIN] Não havia coordenador para matar.")

def matar_processo(proc: Processo):
    remover_thread(proc)
    proc.stop()
    proc.join(timeout=1.0)  


if __name__ == "__main__":
 
    p0 = Processo(randint(0, 10000), threads, threads_lock)
    adicionar_thread(p0)
    p0.start()
    escolher_coordenador()

    Thread(target=criar_processos, daemon=True).start()
    Thread(target=inativar_coordenador, daemon=True).start()

    # mantém a main viva
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print("\n[MAIN] Encerrando...")
        with threads_lock:
            copia = list(threads)
        for t in copia:
            matar_processo(t)
        print("[MAIN] Finalizado.")
