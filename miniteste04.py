# -*- coding: utf-8 -*-
#!/usr/bin/env python
import simpy as SimPy
from random import uniform, seed, randint
import random
import itertools

TEMPO_MEDIO_CHEGADAS = 1.0              # tempo médio entre chegadas sucessivas de clientes
TEMPO_MEDIO_ATENDIMENTO = 0.5           # tempo médio de atendimento no servidor
OCUPADO = False                         # estado do recurso

def main():
    random.seed(25)                                 # semente do gerador de números aleatórios
    ambiente = SimPy.Environment()                  # cria o ambiente do modelo
    servidorRes = SimPy.Resource(ambiente, capacity=1)   # cria o recurso servidorRes
    ambiente.process(gera_cliente(ambiente, servidorRes))             # incia processo de geração de chegadas

    ambiente.run(until=5)                                # executa o modelo por 5 min


def gera_cliente(ambiente,servidorRes):
    contaChegada = 0
    while True:
        yield ambiente.timeout(random.expovariate(1.0/TEMPO_MEDIO_CHEGADAS))
        contaChegada += 1
        print('TEMPO[%.1f]: Chegada do cliente %d' % (ambiente.now, contaChegada))

        # inicia o processo de atendimento
        ambiente.process(atende_cliente(ambiente, "cliente %d" % contaChegada, servidorRes))

def atende_cliente(ambiente,nome,servidorRes):
    # função que ocupa o servidor e realiza o atendimento
    # solicita o recurso servidorRes
    with servidorRes.request() as request:
        # aguarda em fila até a liberação do recurso e o ocupa
        yield request
        OCUPADO = True
        print('TEMPO[%.1f]: Servidor inicia o atendimento do %s' % (ambiente.now, nome))

        # aguarda um tempo de atendimento exponencialmente distribuído
        yield ambiente.timeout(random.expovariate(1.0/TEMPO_MEDIO_ATENDIMENTO))
        OCUPADO = False
        print('TEMPO[%.1f]: Servidor termina o atendimento do %s. Clientes em fila: %i' % (ambiente.now, nome, len(servidorRes.queue)))

def termina_servico():
    if not servico.queue:
        print('[%.3f] Servidor livre' % (ambiente.now))
    else:
        yield ambiente.timeout(uniform(3,7))
        yield ambiente.process(termina_servico())


if __name__ == '__main__':
    main()
