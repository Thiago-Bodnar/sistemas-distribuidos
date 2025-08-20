from time import sleep
from threading import Thread
from ThreadBully import Processo
from random import randint

def criar_processos():
    while True:
        id = randint(0,10000)
        while (id in getIds()):
            print("Id", id, "já existia")
            id = randint(0,1000)

        thread = Processo(id, threads)
        print("Processo",id,"iniciando")
        threads.append(thread)
        thread.start()
        sleep(40)

def inativar_coordenador():
    while True:
        sleep(60)
        for item in threads:
            if item.isCoordenador:
                print("-- Intivando Coordenador: ", item.id)
                matar_processo(item)
                break
def matar_processo(item):
    threads.remove(item)
    item.stop()
    item.join()

def getIds():
    ids = []
    for thread in threads:
        ids.append(thread.id)
    return ids

threads = []

Thread(target = criar_processos).start()
Thread(target = inativar_coordenador).start()
