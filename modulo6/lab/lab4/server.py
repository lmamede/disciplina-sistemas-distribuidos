# Servidor de calculadora usando RPyC
import rpyc
from rpyc.utils.server import ThreadedServer
from rpyc.utils.server import ForkingServer
import multiprocessing
import random

class Calculadora(rpyc.Service):
	'''Classe que oferece operacoes matematicas basicas'''
	exposed_aux=10
	def on_connect(self, conx):
		print("Conexao estabelecida.")
	def on_disconnect(self, conx):
		print("Conexao encerrada.")
	def exposed_soma(self, a, b):
		return a+b
	def exposed_sub (self, a, b):
		return a-b
	def exposed_mult (self, a, b):
		return a*b
	def exposed_div (self, a, b):
		return a/b


class Node():
	"""Representa cada processo criado"""

	def __init__(self, new_id):
		self.id = new_id
		self.port = 10001
		self.calculator = ThreadedServer(Calculadora, port=self.port)
		self.parent = ""
		self.children = []

	def __repr__(self):
		kid = ""
		node_parent = ""
		if self.parent != "":
			node_parent = self.parent.id
		for child in self.children:
			kid += str(child.id) + ","
		return f'id: {self.id} parent: {node_parent} children: {kid}'

	def add_parent(self, parent):
		self.parent = parent

	def add_children(self, child):
		self.children.append(child)

	def get_smallest_child(self):
		"""Faz a busca na arvore pelo processo de menor id"""
		if len(self.children) == 0:
			return self
		elif len(self.children) == 1:
			return self.children[0]
		else:
			process1 = self.children[0].get_smallest_child()
			process2 = self.children[1].get_smallest_child()

			if process1.id > process2.id:
				smallest = process2
			else:
				smallest = process1

			if smallest.id > self.id:
				return self
			return smallest

class ProbeEcho(rpyc.Service):
	last_parent_added = []
	root = []
	def on_connect(self, conx):
		print("Conexao estabelecida.")
	def add_to_queue(self,n):
		"""Na criacao de cada node, para decidir os pais e os filhos dos nos eh gerenciada
		uma fila, o primeiro nó é aquele que é escolhido como pai, quando um nó atinge 2
		filhos, ele deixa de ser elegível e é tirado da lista."""
		if len(self.last_parent_added) > 0:
			parent = self.last_parent_added[0]

			parent.add_children(n)

			n.add_parent(parent)

			self.last_parent_added.append(n)

			if len(parent.children) == 2:
				self.last_parent_added.pop(0)

		else:
			self.last_parent_added.append(n)
			self.root = [n]


	def create_processes(self):
		"""Cria os nós e suas relacoes de pai e filhos"""
		nodes = 6
		for node in range(nodes):
			id = random.random() #gera ids aleatorios entre 0 e 1
			n = Node(id) #instancia novo nó
			self.add_to_queue(n)


	def search_process(self):
		"""Chama os método de busca para recupera o nó de menor id e retorna
		a calculadora desse nó para efetuar o processamento do cliente"""
		smallest = self.root[0].get_smallest_child()
		return smallest

	def new_calculator_server(self,calculadora):
		calculadora.start()


	def exposed_calculadora(self):
		"""Interface chamada pelo cliente para receber uma calculadora"""
		print("Iniciando busca por calculadora...")
		self.create_processes() #cria os processos e escolha o mais adequado para processar o pedido do cliente
		leader_process = self.search_process()
		calculadora = leader_process.calculator

		#inicia um server de calculadora com base no processo lider ganhador
		calculator_server = multiprocessing.Process(target=self.new_calculator_server, args=(calculadora,))
		calculator_server.start()

		print("Busca finalizada, retornando porta do serviço encontrada ", leader_process.port)
		return leader_process.port


probeecho = ForkingServer(ProbeEcho, port=10000)
probeecho.start() 
