import socket
from operator import itemgetter
import json

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
	#esperar por mensagem do lado ativo
	msg = novoSock.recv(1024) #argumento indica quantidade maxima de bytes
	if not msg: break #trata o encerramento da conexao pelo lado ativo

	try:
		name = msg.decode("utf-8")   #decodifica a mensagem
		file = open(name, "r")       #busca o arquivo
		d = dict()
		for line in file:            #percorre linha a linha do arquivo
			line = line.lower()
			line = line.strip()
			words = line.split(" ") #trata a linha e transforma em palavras
			for word in words:      #percorre palavra a palavra da linha
				if word in d and word != "":   #se a palavra ja estiver no dicionario aumenta o numero de ocorrencias
					d[word] = d[word]+1
				else:
					d[word] = 1            #se nao tiver, cria uma entrada pela primeira vez
		res = dict(sorted(d.items(), key=itemgetter(1), reverse=True)[:5]) #reordena o dicionario pelo numero de ocorrencia e retorna apenas os 5 primeiros
		encode_res = json.dumps(res, indent=2).encode('utf-8')             #transforma o dicionario em um json 
		novoSock.send(encode_res)                                          #envia o resultado

	except  FileNotFoundError as e:                                           #trata a inexistencia do arquivo no diretorio
		novoSock.send(bytes("0", "utf-8"))
		continue


#fechar o descritor de socket da conexao
novoSock.close()

#fechar o descritor de socket principal
sock.close()

