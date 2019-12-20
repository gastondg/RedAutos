import string
import random

def patente_generator(cuantas=50):
    patentes = set()
    for i in range(cuantas):
        caracteres = ''.join(random.choice(string.ascii_uppercase) for _ in range(3))
        numeros = ''.join(random.choice(string.digits) for _ in range(3))
        patentes.add(caracteres+numeros)
    return patentes

if __name__ == "__main__":
    print(patente_generator())