import socket

TCP_IP = '192.168.1.35'
TCP_PORT = 5000
BUFFER_SIZE = 1024

def ask_instruction():
    print("entrer le montant en centimes Ex : \"750\" (Ctrl-C pour annuler)")
    cents = input("> ")
    if not (cents == "quit" or cents == "exit" or cents == "quit()"):
        send_instruction(cents)
    
def send_instruction(cents):
    decimales = 0
    if type(cents) != str:
        cents = str(cents)

    for i in [",","."]:
        if i in cents:
            cents = cents.split(i)
            decimales = len(cents[1])
            cents = cents[0]+cents[1]
            if decimales == 0:
                cents = cents+"00"
            if decimales == 1:
                cents = cents+"0"
            if decimales > 2:
                print("trop de decimales")
                cents = None
    if len(cents) > 5 or decimales > 2:
        print("erreur, valeur trop longue")
        cents = None
    while len(cents) < 5:
        cents = "0" + cents
    if cents.isdigit() == False:
        print("que des chiffres, virgule ou point, merci >.<")
        cents = None

    if cents is not None:
        print("je retiens la valeur suivante: ",cents," centimes d'euros")
        MESSAGE = bytes("00000"+cents+"000978", 'utf-8')
        print("j'envoie ",MESSAGE.decode("UTF-8"),"sur ",TCP_IP,":",TCP_PORT)
        print("en attente de la réponse du terminal")

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((TCP_IP, TCP_PORT))
            s.send(MESSAGE)
            data = s.recv(BUFFER_SIZE)
            s.close()
            print("received data:", data, "transaction terminée")
            print("--------------------------------------------")

        except Exception as e:
            print(e)

    else:
        print("erreur cents invalide")