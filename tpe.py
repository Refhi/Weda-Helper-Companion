import socket
from enum import IntEnum

class ProtocolTPE(IntEnum):
    DEFAUT = 0
    CONCERTV3 = 1


BUFFER_SIZE = 1024
    
def send_instruction(ipTPE,portTPE,cents,protocol):
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
        if protocol == ProtocolTPE.DEFAUT: 
            MESSAGE = bytes("00000"+cents+"000978", 'utf-8')

        elif protocol == ProtocolTPE.CONCERTV3: #Protocole Concert V3
            MESSAGE = bytes("CZ0040300CJ012247300123456CA00201CB005"+cents+"CD0010CE003978", 'utf-8')

        else:
            print("protocole non valide")
            return
        print("j'envoie ",MESSAGE.decode("UTF-8"),"sur ",ipTPE,":",portTPE)
        print("en attente de la réponse du terminal")

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((ipTPE, int(portTPE)))
            s.send(MESSAGE)
            data = s.recv(BUFFER_SIZE)
            s.close()
            print("received data:", data, "transaction terminée")
            print("--------------------------------------------")

        except Exception as e:
            print(e)

    else:
        print("erreur cents invalide")

if __name__ == "__main__":
    TCP_IP = '192.168.1.35'
    TCP_PORT = 5000
    send_instruction(TCP_IP,TCP_PORT,0, ProtocolTPE.DEFAUT)