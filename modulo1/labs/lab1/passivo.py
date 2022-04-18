import socket

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
	novoSock.send(msg)


#fechar o descritor de socket da conexao
novoSock.close()

#fechar o descritor de socket principal
sock.close()

