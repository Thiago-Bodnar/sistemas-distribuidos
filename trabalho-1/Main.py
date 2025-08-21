from time import sleep
from threading import Thread
from random import randint, choice
from queue import PriorityQueue
from ThreadBully import Processo

threads = []

def criar_processos():
    while True:
        sleep(40)  # A cada 40s um novo processo
        id = randint(0, 10000)
        while id in getIds():
            print("Id", id, "já existia")
            id = randint(0, 10000)

        thread = Processo(id, threads)
        threads.append(thread)
        thread.start()
        print(f"[MAIN] Processo {id} iniciado")

        # Se não houver coordenador, escolhe um aleatório
        if not any(t.isCoordenador for t in threads):
            escolher_coordenador()

def inativar_coordenador():
    while True:
        sleep(60)  # A cada 1 minuto, coordenador morre
        coord = next((t for t in threads if t.isCoordenador), None)
        if coord:
            print(f"[MAIN] Coordenador {coord.id} morreu")
            matar_processo(coord)

            # Escolher novo coordenador aleatório
            if threads:
                escolher_coordenador()

def escolher_coordenador():
    if threads:
        novo = choice(threads)
        novo.isCoordenador = True
        print(f"[MAIN] Novo coordenador: {novo.id}")
        Thread(target=novo.consumirFila, daemon=True).start()

def matar_processo(proc):
    threads.remove(proc)
    proc.stop()
    proc.join()

def getIds():
    return [t.id for t in threads]

if __name__ == "__main__":
    # Criar a primeira thread manualmente
    p0 = Processo(randint(0,10000), threads)
    threads.append(p0)
    p0.start()
    escolher_coordenador()

    # Start das threads de criação e inativação
    Thread(target=criar_processos, daemon=True).start()
    Thread(target=inativar_coordenador, daemon=True).start()

    # Mantém a main rodando
    while True:
        sleep(1)
