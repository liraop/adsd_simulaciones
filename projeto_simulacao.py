import random
import simpy

class ServidorDNS(object):
    # cria a classe ServidorDNS
    # Um servidor dns tem alta capacidade para processamento de requisições
    # entretanto, por questões apenas de simulação, vamos considerar que o mesmo
    # tem uma capacidade infinita.
    # O tempo de atendimento é praticamente estável.
    def __init__(self, env, duracao, nome):
        # atributos do recurso
        self.nome = nome
        self.env = env
        self.res = simpy.Resource(env)
        self.clientesAtendidos = 0
        self.tempoAtendimento = duracao

    def atendimento(self, cliente):
        # executa o atendimento
        print("[%.1f] %s: Atendendo requisição DNS %s" % (env.now, self.nome, cliente))
        yield self.env.timeout(self.tempoAtendimento)
        print("[%.1f] %s: Requisição DNS processada %s" % (env.now, self.nome, cliente))
        self.clientesAtendidos += 1
        print("[%.1f] %s: Enviando %s ao servidor de dados" % (env.now, self.nome, cliente))


def processaCliente(env, cliente, servidor):
    # função que processa o cliente

    print('[%.1f] Chegada do %s ao sistema' % (env.now, cliente))
    with servidor.res.request() as req: # note que o Resource é um atributo também
        yield req

        print('[%.1f] %s: %s requer atendimento' % (env.now, servidor.nome, cliente))
        yield env.process(servidor.atendimento(cliente))
        print('[%.1f] %s: %s desocupa o servidor' % (env.now, servidor.nome, cliente))


def geraClientesDNS(env, intervalo, servidores_dns):
    # função que gera os clientes
    # Os servidores DNS do sistema funcionam com balanceamento de carga da seguinte maneira:
    # As requisições seguem normalmente para o ServidorDNS1 até o mesmo obter 70% de load
    # ou ficar indisponível. O ServidorDNS2 então assumiria o papel, refletindo esse esquema
    # com o ServidorDNS3.
    i = 0
    while True:
        yield env.timeout(random.expovariate(1.0/intervalo))
        probabilidade_dns = random.uniform(0,1)
        i += 1
        if probabilidade_dns < 0.7:
            env.process(processaCliente(env, 'cliente %d' % i, servidores_dns[0]))
        elif (0.7 <= probabilidade_dns < 0.9):
            env.process(processaCliente(env, 'cliente %d' % i, servidores_dns[1]))
        else:
            env.process(processaCliente(env, 'cliente %d' % i, servidores_dns[2]))


random.seed(1000)
env = simpy.Environment()
servidores_dns = [ServidorDNS(env, 3, "DNS1"),ServidorDNS(env,4,"DNS2"),ServidorDNS(env, 1,"DNS3")]
env.process(geraClientesDNS(env,2,servidores_dns))


env.run(until=500)
