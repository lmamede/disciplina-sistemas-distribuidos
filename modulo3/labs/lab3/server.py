import socket
from operator import itemgetter
import json

#Trata erro caso arquivo nao seja encontrado
def treatError(novoSock):
	novoSock.send(bytes("0", 'utf-8'))

#Decodifica a mensagem e busca o arquivo
def findFile(msg, novoSock):
	try:
		name = msg.decode("utf-8")
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

HOST = '' #interface padrao de comunicacao da maquina
PORTA = 5000 #identifica o processo na maquina

#criar o descritor socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #internet e TCP

#vincular o endereco e porta
sock.bind((HOST, PORTA))

#colocar-se em modo de espera 
sock.listen(1) #argumento indica a quantidade de conexoes pendentes

#aceitar conexao
novoSock, endereco = sock.accept()
print('Conectado com: ' + str(endereco))



while True: #fica em loop esperando pelo ativo

	msg = novoSock.recv(1024) #argumento indica quantidade maxima de bytes
	if not msg: break #trata o encerramento da conexao pelo lado ativo

	try:
		file = findFile(msg, novoSock)
		if file == None: continue
		processFile(novoSock, file)
	except:
		print("Erro! Desligando servidor...")
		break

#fechar o descritor de socket da conexao
novoSock.close()

#fechar o descritor de socket principal
sock.close()


