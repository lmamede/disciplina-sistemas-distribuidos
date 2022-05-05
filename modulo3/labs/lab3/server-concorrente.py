import socket
from operator import itemgetter
import json
import select
import sys
import threading


HOST = '' #interface padrao de comunicacao da maquina
PORTA = 5000 #identifica o processo na maquina

inputs = [sys.stdin]
conn = {}
threadClients = []

lock = threading.Lock()

#Trata erro caso arquivo nao seja encontrado
def treatError(novoSock):
	novoSock.send(bytes("0", 'utf-8'))

#Decodifica a mensagem e busca o arquivo
def findFile(msg, novoSock):
	try:
		name = msg.decode("utf-8")
		print("[",conn[novoSock],"] Buscando arquivo", msg)

		file = open(name, "r")
		return file
	except:
		treatError(novoSock)
		return None

def processFile(novoSock, file):
	d = dict()
	for line in file:                         #percorre linha a linha do arquivo
		words = prepareWords(line)
		for word in words:                #percorre palavra a palavra da linha
			computeOccurence(word, d)
	novoSock.send(packResults(d))             #envia o resultado

#Trata a linha para extrair as palavras
def prepareWords(line):
	line = line.lower()
	line = line.strip()
	words = line.split(" ")
	return words

#Verifica se a palavra ja consta no dicionario
#se sim, incrementa ocorrencia
#se nao, adiciona uma nova entra com a primeira ocorrencia
def computeOccurence(word, d):
	if word in d and word != "":
		d[word] = d[word]+1
	else:
		d[word] = 1

#Reordena o dicionario pelo numero de ocorrencias
#retornar os 5 primeiros
#empacota em um json
def packResults(d):
	res = dict(sorted(d.items(), key=itemgetter(1), reverse=True)[:5])
	encode_res = json.dumps(res, indent=2).encode('utf-8')
	return encode_res


def prepareServer():
	#criar o descritor socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #internet e TCP

	#vincular o endereco e porta
	sock.bind((HOST, PORTA))

	#colocar-se em modo de espera 
	sock.listen(1) #argumento indica a quantidade de conexoes pendentes

	sock.setblocking(False)
	inputs.append(sock)

	return sock

#Criando conexao com cliente 
#adiciona as informacoes dos clientes no dicionario
#inicia a thread e aloca a referencia em threadClients
def startClient(sock):
	global conn

	client, addr = sock.accept()
	print('Conectado com: ' + str(addr))

	lock.acquire()
	conn[client] = addr
	lock.release()

	threadClient = threading.Thread(target=startFileFinderService, args=(client,))
	threadClient.start()
	threadClients.append(threadClient)

#Encerra cliente
#Exclui cliente do dicionario
def stopClient(client):
	global conn

	lock.acquire()
	if len(conn) > 0: 
		del conn[client]

	lock.release()
	client.close()
	print("[INFO] Conexao encerrada!")

#recebe entrada do cliente
#se vazia, encerra o cliente
#se nao, busca o arquivo e processa as ocorrencias
#em caso de erro nas etapas anteriores, encerra o cliente
def startFileFinderService(client):
	try:
		while True:
			msg = client.recv(1024) #argumento indica quantidade maxima de bytes

			if not msg: 
				print("[INFO] Cliente encerrou conexao")
				stopClient(client) 
				return 

			file = findFile(msg, client)
			if file != None: processFile(client, file)
	except:	
		print("[ERROR] Erro ao receber entrada. Encerrando conexao com cliente!")
		stopClient(client)
#Menuzinho de interacao com o servidor
#oferece os comandos para encerrar
#derrubar as conexoes encerrando os clientes
#mostra o total de clientes ativos
#oferece um manual dos comandos
def startServerConsoleService(sock):
	global conn
	command = input()
	if command == 'stop':
		if len(conn) == 0:
			print("Encerrando servidor")
			sock.close()
			sys.exit()
		else:
			print("[WARN] Existem conexoes ativas, aguarde e tente novamente mais tarde.")
	if command == 'connections':
		print(">>> Existem ",len(conn), " conexoes ativas")

	if command == 'drop':
		print("[INFO] Derrubando todas as conexoes")
		for client in threadClients:
			client.join()
		conn.clear()
		threadClients.clear()
		print("[INFO] Conexoes derrubadas")

	if command == 'help':
		print("\n\tstop: para o server",\
		"\n\tconnections: mostra quantidade de conexões ativas",\
		"\n\tdrop: derruba todas as conexoes ativas",\
		"\n\thelp: mostra esse painel")

sock = prepareServer()

print("Bem vindo ao console de administrador do server,"\
"\ndigite help para mostrar as opcoes de gerenciamento")

while True: #fica em loop esperando entrada
	try:
		r, w, e = select.select(inputs, [], [])
		for request in r:
			if request == sock: #se for um cliente novo, inicia 
				startClient(sock)

			elif request == sys.stdin: #se for um input, abre o console
				startServerConsoleService(sock)

	except:
		print("Erro! Desligando servidor...")
		break

#fechar o descritor de socket principal
sock.close()


