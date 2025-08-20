from threading import Thread
from time import sleep
from queue import PriorityQueue
from Request import Request
from datetime import datetime

class Processo(Thread):

    coordenador = None
    isCoordenador = False

    filaCoordenador = PriorityQueue()

    isRunning = True

    possuiEleicaoEmAndamento = False

    def _init_(self, id, threads):
        super()._init_()
        self.id = id
        self.threads = threads
        try: 
            self.coordenador = next(filter(lambda x: (x is not None) and (x.coordenador is not None), threads)).coordenador
        except StopIteration:
            self.coordenador = None
    def run(self):
        while self.isRunning:
            self.request_coordenador()
            sleep(10)

    def request_coordenador(self):
        print("Processo ", self.id, " fez uma request para ", self.coordenador.id if self.coordenador is not None else "Nenhum")
        if self.coordenador is None:
            print("Processo ", self.id, " não possui coordenador")
            self.iniciar_eleicao()
        else:
            if not self.coordenador.request(Request(self.id, datetime.now())):
                print("Processo ", self.id, " não recebeu resposta do coordenador")
                self.iniciar_eleicao()
            
    def iniciar_eleicao(self):
        if not Processo.possuiEleicaoEmAndamento:
            Processo.possuiEleicaoEmAndamento = True
            print("Thread ", self.id, " iniciou uma eleicao")
            Thread(target = self.eleicao).start()
        else:
            print("Processo ", self.id, " Já havia outra eleição")
    
    def eleicao(self):
        resultado = False
        for item in self.threads:
            if item.id > self.id:
                try:
                    resultado = item.request(Request(item.id, datetime.now()))
                    Thread(target = item.eleicao()).start()
                except:
                    pass
        if not resultado and Processo.possuiEleicaoEmAndamento:
            Processo.possuiEleicaoEmAndamento = False
            self.coordenador = self
            self.isCoordenador = True
            print("-- O coordenador eleito é: ", self.id)
            for item in self.threads:
                item.coordenador = self
            Thread(target = self.consumirFila()).start()
    
    def consumirFila(self):
        while self.isRunning:
            if not self.filaCoordenador.empty():
                request = self.filaCoordenador.get()
                print("Consumindo recurso requisitado pelo processo: ", request.id, " no tempo ", request.time.strftime("%H:%M:%S"))
                sleep(10)
    
    def request(self, request):
        if self.isCoordenador and self.isRunning:
            self.filaCoordenador.put(request)
        return self.isRunning

    def stop(self):
        while not self.filaCoordenador.empty():
            self.filaCoordenador.get(False)
        self.isRunning  = False
