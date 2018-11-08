"# -*- coding: utf-8 -*-"
import random
import simpy

TAXA_ATENDIMENTO_DNS1 = 1
TAXA_ATENDIMENTO_DNS2 = 1.5
TAXA_ATENDIMENTO_DNS3 = 1.8
TAXA_ATENDIMENTO_HOST_LINUX = 0.5
TAXA_ATENDIMENTO_PROXYAPACHE = 0.1
TAXA_ATENDIMENTO_CONTAINERS = 0.4
TAXA_ENTRADA_CLIENTE = 2

def processaCliente(env, cliente, servidor):
    print("%s --- Status \n Clientes em fila: %d \n Clientes atendidos: %d" % (servidor.nome, len(servidor.res.queue), servidor.clientesAtendidos))
    print('[%.3f] %s: %s chegou.' % (env.now, servidor.nome, cliente.nome))
    with servidor.res.request() as req:
        yield req
        print('[%.3f] %s: %s requer atendimento' % (env.now, servidor.nome, cliente.nome))
        yield env.process(servidor.atendimento(cliente))
        print('[%.3f] %s: %s saiu.' % (env.now, servidor.nome, cliente.nome))


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
            env.process(processaCliente(env, Cliente('Cliente %d' % i, env.now), servidores_dns[0]))
        elif (0.7 <= probabilidade_dns < 0.9):
            env.process(processaCliente(env, Cliente('Cliente %d' % i, env.now), servidores_dns[1]))
        else:
            env.process(processaCliente(env, Cliente('Cliente %d' % i, env.now), servidores_dns[2]))

class Cliente(object):
    def __init__(self, nome, tempo_entrada_sistema):
        self.nome = nome
        self.tempo_entrada_sistema = tempo_entrada_sistema
        self.tempo_saida_sistema = 0

    def setTempoSaida(self, tempo):
        self.tempo_saida_sistema = tempo

    def get_tempo_total_atendimento(self):
        return self.tempo_saida_sistema - self.tempo_entrada_sistema

class ServidorDNS(object):
    # cria a classe ServidorDNS
    # Um servidor dns tem alta capacidade para processamento de requisições
    # entretanto, por questões apenas de simulação, vamos considerar que o mesmo
    # tem uma capacidade infinita.
    # O tempo de atendimento é praticamente estável, variando pouco.
    # O DNS precisa saber para qual servidor enviar a requisição após o processamento.
    def __init__(self, env, duracao, nome, proxyApache):
        # atributos do recurso
        self.nome = nome
        self.env = env
        self.res = simpy.Resource(env, capacity =1)
        self.clientesAtendidos = 0
        self.tempoAtendimento = random.expovariate(1.0/duracao)
        self.proxyApache = proxyApache

    def atendimento(self, cliente):
        # executa o atendimento
        print("[%.3f] %s: Atendendo requisição DNS %s" % (env.now, self.nome, cliente.nome))
        yield self.env.timeout(self.tempoAtendimento)
        print("[%.3f] %s: Requisição DNS processada %s" % (env.now, self.nome, cliente.nome))
        self.clientesAtendidos += 1
        print("[%.3f] %s: Enviando %s ao servidor de dados" % (env.now, self.nome, cliente.nome))
        yield self.env.process(processaCliente(self.env, cliente, self.proxyApache))


class HostLinux(object):
    # cria a classe HostLinux
    # Seguindo o modelo do sistema, após conhecer o nome do serviço, o DNS
    # envia a requisição do cliente para um Host Linux onde rodam os outros
    # serviços necessários ao sistema.
    # HostLinux roda uma instância do Docker com dois containers e o proxyApache.
    # ProxyApache redireciona os requests HTTP para o container correto.
    #
    def __init__(self, env, duracao, nome, dockerEngine):
        self.nome = nome
        self.env = env
        self.res = simpy.Resource(env, capacity=1)
        self.clientesAtendidos = 0
        self.tempoAtendimento = duracao
        self.dockerEngine = dockerEngine

    def atendimento(self, cliente):
        tempo_chegada = env.now
        yield self.env.timeout(random.expovariate(1.0/self.tempoAtendimento))
        self.clientesAtendidos += 1
        tempo_processamento = env.now - tempo_chegada
        print("[%.3f] %s: Requisição do %s processada em %.1f u.t." % (env.now, self.nome, cliente.nome, tempo_processamento))
        print("[%.3f] %s: Requisição do %s encaminhada para o Docker Engine" % (env.now, self.nome, cliente.nome))
        yield self.env.process(processaCliente(self.env, cliente, self.dockerEngine))

class DockerEngine(object):
    # cria a classe dockerEngine
    # O dockerEngine age como um central de controle para os containers.
    # Ela gerencia a execução dos mesmos e intermedia as operações de
    # escrita e leitura de dados no host.
    # Tem desempenho afetado pela quantidade de containers.
    def __init__(self, env, nome, containers):
        self.nome = nome
        self.env = env
        self.res = simpy.Resource(env, capacity=1)
        self.tempoAtendimento = random.expovariate(1.0/len(containers))
        self.containers = containers
        self.clientesAtendidos = 0

    def atendimento(self, cliente):
        tempo_chegada = env.now
        yield self.env.timeout(self.tempoAtendimento)
        self.clientesAtendidos += 1
        tempo_processamento = env.now - tempo_chegada
        print("[%.3f] %s: Requisição do %s processada em %.1f u.t." % (env.now, self.nome, cliente.nome, tempo_processamento))
        print("[%.3f] %s: Requisição do %s encaminhada para %s" % (env.now, self.nome, cliente.nome, self.containers[0].nome))
        yield self.env.process(processaCliente(self.env, cliente, self.containers[0]))
        print("[%.3f] %s: Requisição do %s encaminhada para %s" % (env.now, self.nome, cliente.nome, self.containers[1].nome))
        yield self.env.process(processaCliente(self.env, cliente, self.containers[1]))
        print("[%.3f] %s: Respondendo ao %s." % (env.now, self.nome, cliente.nome))

class Container(object):
    # cria a classe container
    def __init__(self, env, nome, dataVolume, duracao):
        self.nome = "Container %s" % nome
        self.env = env
        self.clientesAtendidos = 0
        self.res = simpy.Resource(env, capacity=1)
        # tempo de atendimento maior se for container de dados, isto é, precisar acessar o disco
        self.tempoAtendimento = (random.expovariate(1.0/duracao) if dataVolume else random.expovariate(10.0/duracao))

    def atendimento(self, cliente):
        tempo_chegada = env.now
        yield self.env.timeout(self.tempoAtendimento)
        self.clientesAtendidos += 1
        tempo_processamento = env.now - tempo_chegada
        print("[%.3f] %s: Requisição do %s processada em %.1f u.t." % (env.now, self.nome, cliente.nome, tempo_processamento))
        print("[%.3f] %s: Requisição do %s devolvida ao cliente." % (env.now, self.nome, cliente.nome))
        cliente.setTempoSaida(env.now)
        print("Tempo total de atendimento ao %s: %.4f" % (cliente.nome, cliente.get_tempo_total_atendimento()))



random.seed(1000)
env = simpy.Environment()

dockerEngine = DockerEngine(env, "dockerEngine", [Container(env, "Node", False, TAXA_ATENDIMENTO_CONTAINERS), Container(env, "MySQL", True, TAXA_ATENDIMENTO_CONTAINERS)])
proxyApache = HostLinux(env, TAXA_ATENDIMENTO_PROXYAPACHE, "proxyApache", dockerEngine)
servidores_dns = [ServidorDNS(env, TAXA_ATENDIMENTO_DNS1, "DNS1", proxyApache),ServidorDNS(env, TAXA_ATENDIMENTO_DNS2,"DNS2", proxyApache),ServidorDNS(env, TAXA_ATENDIMENTO_DNS3,"DNS3", proxyApache)]
env.process(geraClientesDNS(env, TAXA_ENTRADA_CLIENTE, servidores_dns))

env.run(until=500)
