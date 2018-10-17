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
    ambiente.process(gera_cliente())
    ambiente.process(recebe_cliente())
    ambiente.process(termino_servico())

    print('Simulação iniciada')
    ambiente.run(until=200)
    print('Simulação completa')

def gera_cliente():
    PRIORIDADE_ALTA = 1

    cliente = (id, classe) =  'Cliente %s' % randint(1,1000), randint(1,2)

    proxima_entrada = 0

    if (cliente[1] == PRIORIDADE_ALTA):
        print('Entrada cliente classe 1 as %.3f' % ambiente.now)
        proxima_entrada = uniform(1,10)
    else:
        print('Entrada cliente classe 2 as %.3f' % ambiente.now)
        proxima_entrada = uniform(1,5)

    yield ambiente.timeout(proxima_entrada)
    print('Próxima entrada escalonada para daqui a %.2f ts' % proxima_entrada)

def recebe_cliente():
    if (servico.count == 0 ):
        print("Cliente sendo processado em %.3f" % ambiente.now)
    else:
        print("Cliente enviado para fila em %.3f" % ambiente.now)
        with servico.request(cliente[0], priority=cliente[1]) as req:
            yield req


def termino_servico():
    if not servico.queue:
        print("Servidor livre")
    else:
        print(servico.queue)
        yield ambiente.timeout(uniform(3,7))
        servico.release()

if __name__ == '__main__':
    main()
