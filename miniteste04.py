# -*- coding: utf-8 -*-
#!/usr/bin/env python
import simpy as SimPy
from random import uniform, seed, randint
import itertools

ambiente = SimPy.Environment()
servico = SimPy.PriorityResource(ambiente, capacity=1)
status = ''

def main():
    status = 'Livre'
    ambiente.process(gera_cliente(status))
    #ambiente.process(recebe_clinte())
    #ambiente.process(atende_cliente())
    #ambiente.process(termina_servico())

    print('Simulação iniciada')
    ambiente.run(until=100)
    print('Simulação completa')

def gera_cliente(status):
    while True:
        PRIORIDADE_ALTA = 1

        cliente = (id, classe) =  'Cliente %s' % randint(1,1000), randint(1,2)

        proxima_entrada = 0

        if (cliente[1] == PRIORIDADE_ALTA):
            proxima_entrada = uniform(1,10)
        else:
            proxima_entrada = uniform(1,5)

        if (status == 'Livre'):
            yield ambiente.process(atende_cliente(cliente))
        else:
            yield ambiente.process(enfileira_cliente(cliente))

        yield ambiente.timeout(proxima_entrada)
        print('[%.3f] Próxima entrada escalonada para daqui a %.2f ts' % (ambiente.now, proxima_entrada))

def atende_cliente(cliente):
    print('[%.3f] %s sendo atendido' % (ambiente.now, cliente[0]))
    tempo_atendimento = uniform(5,10)
    yield ambiente.timeout(tempo_atendimento)
    print('[%.3f] %s atendido em %.2f tps' % (ambiente.now, cliente[0], tempo_atendimento))

def enfileira_cliente(cliente):
    print('[%.3f] Servidor ocupado. %s enfileirado.' % (ambiente.now, cliente[0]))


def termina_servico():
    if not servico.queue:
        print('[%.3f] Servidor livre' % (ambiente.now))
    else:
        yield ambiente.timeout(uniform(3,7))
        yield ambiente.process(termina_servico())


if __name__ == '__main__':
    main()
