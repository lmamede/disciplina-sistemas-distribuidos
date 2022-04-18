import socket

#identifica a comunica com o lado passivo
HOST = 'localhost' 
PORTA =  5000

#criar o descritor de socket
sock = socket.socket() #AF_INET, SOCK_STREAM ja eh o padrao

#estabelecer conexao
sock.connect((HOST, PORTA)) #nao ganha um novo socket

#receber a mensagem digitada pelo usuario
print('Digite uma mensagem: ')
entrada = input()

while entrada != 'f':
	#enviar mensagem de hello
	sock.send(bytes(entrada, 'utf-8'))

	#receber resposta do lado passivo
	msg = sock.recv(1024)
	print(str(msg, encoding='utf-8'))

	print('Digite uma mensagem: ')
	entrada = input()



#encerrar a conexao
sock.close()
