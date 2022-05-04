import socket
import json

#identifica a comunica com o lado passivo
HOST = 'localhost' 
PORTA =  5000

#criar o descritor de socket
sock = socket.socket() #AF_INET, SOCK_STREAM ja eh o padrao

#estabelecer conexao
sock.connect((HOST, PORTA)) #nao ganha um novo socket

#receber a mensagem digitada pelo usuario
print('Digite o nome do texto: ')
entrada = input()

while entrada != 'f':
	#enviar mensagem de hello
	sock.send(bytes(entrada, 'utf-8'))

	#receber resposta do lado passivo
	msg = sock.recv(1024)
	result = msg.decode('utf-8')

	if(result == "0"):
		print("ERRO: Arquivo não encontrado!")
	else:
		print(result)
	
	
	print('Digite o nome do texto: ')
	entrada = input()



#encerrar a conexao
sock.close()
