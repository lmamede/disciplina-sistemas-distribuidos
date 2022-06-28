# Cliente de calculadora usando RPyC
import rpyc
import threading

def connect_calculator_server(calc_port):
	calc = rpyc.connect('localhost', calc_port)

	while True:
		op = input("Digite uma operacao(+,-,*,/, ou 'fim' para terminar):")
		if op == 'fim':
			calc.close()
			break
		arg1 = int(input("Arg 1:"))
		arg2 = int(input("Arg 2:"))
		if op == '+':
			soma = calc.root.soma(arg1, arg2)
			print(soma)
		elif op == '-':
			sub = calc.root.sub(arg1, arg2)
			print(sub)
		elif op == '*':
			mult = calc.root.mult(arg1, arg2)
			print(mult)
		elif op == '/':
			div = calc.root.div(arg1, arg2)
			print(div)




probe = rpyc.connect('localhost', 10000) #conecta ao server de probe/echo
print(probe.root)
calc_port = probe.root.exposed_calculadora() #recebe a porta do processo lider que gerenciara a calculadora
probe.close()

#conecta ao server calculadora lider
calculator_client = threading.Thread(target=connect_calculator_server, args=(calc_port,))
calculator_client.start()

calculator_client.join()
