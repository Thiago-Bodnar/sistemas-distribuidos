from datetime import datetime
from queue import PriorityQueue
from threading import Thread
from time import sleep
from random import randint
from Request import Request

class Processo(Thread):

    def __init__(self, id, threads):
        super().__init__()
        self.id = id
        self.threads = threads
        self.coordenador = None
        self.isCoordenador = False
        self.filaCoordenador = PriorityQueue()
        self.isRunning = True

    def run(self):
        while self.isRunning:
            sleep(randint(10, 25))  # intervalo 10-25s
            self.request_coordenador()

    def request_coordenador(self):
        coord = next((t for t in self.threads if t.isCoordenador), None)
        if coord is None:
            print(f"[{self.id}] Não há coordenador no momento.")
            return
        print(f"[{self.id}] fez uma requisição para o coordenador {coord.id}")
        coord.receive_request(Request(self.id, datetime.now()))

    def receive_request(self, request):
        if self.isCoordenador and self.isRunning and self.filaCoordenador:
            self.filaCoordenador.put(request)

    def consumirFila(self):
        while self.isRunning and self.isCoordenador:
            if not self.filaCoordenador.empty():
                req = self.filaCoordenador.get()
                print(f"[COORD {self.id}] Consumindo recurso do processo {req.process_id} às {req.timestamp.strftime('%H:%M:%S')}")
                sleep(randint(5, 15))  # processamento 5-15s

    def stop(self):
        self.isRunning = False
        if self.isCoordenador and self.filaCoordenador:
            with self.filaCoordenador.mutex:
                self.filaCoordenador.queue.clear()
