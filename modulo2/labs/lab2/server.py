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
		name = msg.decode("utf-8")
		file = open(name, "r")
		d = dict()
		for line in file:
			line = line.lower()
			line = line.strip()
			words = line.split(" ")
			for word in words:
				if word in d and word != "":
					d[word] = d[word]+1
				else:
					d[word] = 1
		res = dict(sorted(d.items(), key=itemgetter(1), reverse=True)[:5])
		encode_res = json.dumps(res, indent=2).encode('utf-8')
		novoSock.send(encode_res)

	except  FileNotFoundError as e:
		novoSock.send("0")
		break


#fechar o descritor de socket da conexao
novoSock.close()

#fechar o descritor de socket principal
sock.close()

