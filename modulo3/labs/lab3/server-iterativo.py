import socket
from operator import itemgetter
import json
import select
import sys

HOST = '' #interface padrao de comunicacao da maquina
PORTA = 5000 #identifica o processo na maquina

inputs = [sys.stdin]
conn = {}

#Trata erro caso arquivo nao seja encontrado
def treatError(novoSock):
	novoSock.send(bytes("0", 'utf-8'))

#Decodifica a mensagem e busca o arquivo
def findFile(msg, novoSock):
	try:
		name = msg.decode("utf-8")
		print("Buscando arquivo", msg)

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

def startClient(sock):
	global conn

	client, addr = sock.accept()
	print('Conectado com: ' + str(addr))
	client.setblocking(False)
	conn[client] = addr
	inputs.append(client)

def stopClient(client):
	global conn

	client.close()
	if len(conn) > 0: 
		del conn[client]
	inputs.remove(client)


def startFileFinderService(client):
	try:
		#aceitar conexao
		msg = client.recv(1024) #argumento indica quantidade maxima de bytes
		if not msg: return #trata o encerramento da conexao pelo lado ativo

		file = findFile(msg, client)
		if file != None: processFile(client, file)
	except:	
		stopClient(client)

def startServerConsoleService(sock):
	global conn
	command = input()
	if command == 'stop':
		if len(conn) == 0:
			sock.close()
			sys.exit()
		else:
			print("Existem conexoes ativas, aguarde e tente novamente mais tarde.")
	if command == 'connections':
		print("Existem ",len(conn), " conexoes ativas")

	if command == 'drop':
		print("Derrubando todas as conexoes")
		conn.clear()

	if command == 'help':
		print("\n\tstop: para o server",\
		"\n\tconnections: mostra quantidade de conexões ativas",\
		"\n\tdrop: derruba todas as conexoes ativas",\
		"\n\thelp: mostra esse painel")

sock = prepareServer()

print("Bem vindo ao console de administrador do server,"\
"\ndigite help para mostrar as opcoes de gerenciamento")

while True: #fica em loop esperando pelo ativo
	try:
		r, w, e = select.select(inputs, [], [])
		for request in r:
			if request == sock:
				startClient(sock)

			elif request == sys.stdin:
				startServerConsoleService(sock)

			else:
				startFileFinderService(request)

	except:
		print("Erro! Desligando servidor...")
		break

#fechar o descritor de socket principal
sock.close()


