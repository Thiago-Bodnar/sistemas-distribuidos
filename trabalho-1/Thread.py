from datetime import datetime
from queue import PriorityQueue
from threading import Thread, Lock
from time import sleep
from random import randint
from Request import Request

class Processo(Thread):
    def __init__(self, pid: int, threads_ref: list, threads_lock: Lock):
        super().__init__(daemon=True)
        self.id = pid
        self.threads = threads_ref         
        self.threads_lock = threads_lock    
        self.isCoordenador = False
        self.isRunning = True

        self._fila = PriorityQueue()
        self._consumer_thread = None

    def run(self):
        while self.isRunning:
            sleep(randint(10, 25)) 
            self.request_coordenador()

    def request_coordenador(self):
        coord = self._get_coordenador()
        if coord is None:
            print(f"[{self.id}] Não há coordenador no momento.")
            return

        req = Request(self.id, datetime.now())
        print(f"[{self.id}] requisitou RC ao coordenador {coord.id} às {req.timestamp.strftime('%H:%M:%S')}")
        coord.receive_request(req)

    def set_as_coordenador(self):
        self.isCoordenador = True
        print(f"[COORD {self.id}] Assumiu coordenação. Iniciando fila vazia.")
        self._consumer_thread = Thread(target=self._consumir_fila, daemon=True)
        self._consumer_thread.start()

    def receive_request(self, request: Request):
        if self.isCoordenador and self.isRunning:
            self._fila.put(request)

    def _consumir_fila(self):
        while self.isRunning and self.isCoordenador:
            if not self._fila.empty():
                req = self._fila.get()
                inicio = datetime.now()
                print(f"[COORD {self.id}] Concedendo RC ao processo {req.process_id} "
                      f"(chegou {req.timestamp.strftime('%H:%M:%S')}) às {inicio.strftime('%H:%M:%S')}")
                sleep(randint(5, 15)) 
                fim = datetime.now()
                print(f"[COORD {self.id}] Liberou RC do processo {req.process_id} às {fim.strftime('%H:%M:%S')}")
            else:
                sleep(0.1) 

    def stop(self):
        if self.isCoordenador:
            print(f"[COORD {self.id}] Encerrando; descartando fila.")
            with self._fila.mutex:
                self._fila.queue.clear()

        self.isRunning = False
        self.isCoordenador = False

    def _get_coordenador(self):
        with self.threads_lock:
            for t in self.threads:
                if t.isCoordenador:
                    return t
        return None
